#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Pelix remote services: Multicast discovery and event notification

A discovery packet contains the access to the dispatcher servlet, which
can be used to get the end points descriptions.
An event notification packet contain an end point UID, a kind of event and the
previous service properties (if the event is an update).

**WARNING:** Do not forget to open the UDP ports used for the multicast, even
when using remote services on the local host only.

:author: Thomas Calmant
:copyright: Copyright 2013, isandlaTech
:license: GPLv3
:version: 0.1
:status: Alpha

..

    This file is part of iPOPO.

    iPOPO is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    iPOPO is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with iPOPO. If not, see <http://www.gnu.org/licenses/>.
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(map(str, __version_info__))

# Documentation strings format
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------

# Pelix utilities
from pelix.utilities import to_bytes, to_str

# Remote Services constants
import pelix.remote

# iPOPO decorators
from pelix.ipopo.decorators import ComponentFactory, Requires, Provides, \
    Invalidate, Validate, Property

# Standard library
import logging
import json
import os
import select
import socket
import struct
import sys
import threading

if sys.version_info[0] < 3:
    import httplib

else:
    import http.client as httplib


# ------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------

if os.name == "nt":
    # Windows Specific code
    def pton(family, address):
        """
        Calls inet_pton
        
        :param family: Socket family
        :param address: A string address
        :return: The binary form of the given address
        """
        if family == socket.AF_INET:
            return socket.inet_aton(address)

        elif family == socket.AF_INET6:
            # Do it using WinSocks
            import ctypes
            winsock = ctypes.windll.ws2_32

            # Prepare structure
            class sockaddr_in6(ctypes.Structure):
                _fields_ = [("sin6_family", ctypes.c_short),
                            ("sin6_port", ctypes.c_ushort),
                            ("sin6_flowinfo", ctypes.c_ulong),
                            ("sin6_addr", ctypes.c_ubyte * 16),
                            ("sin6_scope_id", ctypes.c_ulong)]

            # Prepare pointers
            addr_ptr = ctypes.c_char_p(to_bytes(address))

            out_address = sockaddr_in6()
            size = len(sockaddr_in6)
            size_ptr = ctypes.pointer(size)

            # Second call
            winsock.WSAStringToAddressA(addr_ptr, family, 0,
                                        out_address, size_ptr)

            # Convert the array...
            bin_addr = 0
            for part in out_address.sin6_addr:
                bin_addr = bin_addr * 16 + part

            return bin_addr

        else:
            raise ValueError("Unhandled socket family: {0}".format(family))

else:
    # Other systems
    def pton(family, address):
        """
        Calls inet_pton
        
        :param family: Socket family
        :param address: A string address
        :return: The binary form of the given address
        """
        return socket.inet_pton(family, address)

# ------------------------------------------------------------------------------

def make_mreq(family, address):
    """
    Makes a mreq structure object for the given address and socket family.
    
    :param family: A socket family (AF_INET or AF_INET6)
    :param address: A multicast address (group)
    :raise ValueError: Invalid family or address
    """
    if not address:
        raise ValueError("Empty address")

    # Convert the address to a binary form
    group_bin = pton(family, address)

    if family == socket.AF_INET:
        # IPv4
        # struct ip_mreq
        # {
        #     struct in_addr imr_multiaddr; /* IP multicast address of group */
        #     struct in_addr imr_interface; /* local IP address of interface */
        # };
        # "=I" : Native order, standard size unsigned int
        return group_bin + struct.pack("=I", socket.INADDR_ANY)

    elif family == socket.AF_INET6:
        # IPv6
        # struct ipv6_mreq {
        #    struct in6_addr ipv6mr_multiaddr;
        #    unsigned int    ipv6mr_interface;
        # };
        # "@I" : Native order, native size unsigned int
        return group_bin + struct.pack("@I", 0)

    raise ValueError("Unknown family {0}".format(family))

# ------------------------------------------------------------------------------

def create_multicast_socket(address, port):
    """
    Creates a multicast socket according to the given address and port.
    Handles both IPv4 and IPv6 addresses.
    
    :param address: Multicast address/group
    :param port: Socket port
    :return: A tuple (socket, listening address)
    :raise ValueError: Invalid address or port
    """
    # Get the information about a datagram (UDP) socket, of any family
    try:
        addrs_info = socket.getaddrinfo(address, port, socket.AF_UNSPEC,
                                       socket.SOCK_DGRAM)
    except socket.gaierror:
        raise ValueError("Error retrieving address informations ({0}, {1})" \
                         .format(address, port))

    if len(addrs_info) > 1:
        _logger.debug("More than one address information found. "
                      "Using the first one.")

    # Get the first entry : (family, socktype, proto, canonname, sockaddr)
    addr_info = addrs_info[0]

    # Only accept IPv4/v6 addresses
    if addr_info[0] not in (socket.AF_INET, socket.AF_INET6):
        # Unhandled address family
        raise ValueError("Unhandled socket family : %d" % (addr_info[0]))

    # Prepare the socket
    sock = socket.socket(addr_info[0], socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Reuse address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, 'SO_REUSEPORT'):
        # Special for MacOS
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Bind the socket
    if sock.family == socket.AF_INET:
        # IPv4 binding
        sock.bind(('0.0.0.0', port))

    else:
        # IPv6 Binding
        sock.bind(('::', port))

    # Prepare the mreq structure to join the group
    # addrinfo[4] = (addr,port)
    mreq = make_mreq(sock.family, addr_info[4][0])

    # Join the group
    if sock.family == socket.AF_INET:
        # IPv4
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Allow multicast packets to get back on this host
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    else:
        # IPv6
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

        # Allow multicast packets to get back on this host
        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, 1)

    return (sock, addr_info[4][0])


def close_multicast_socket(sock, address):
    """
    Cleans up the given multicast socket.
    Unregisters it of the multicast group.
    
    Parameters should be the result of create_multicast_socket
    
    :param sock: A multicast socket
    :param address: The multicast address used by the socket
    """
    if sock is None:
        return

    if address:
        # Prepare the mreq structure to join the group
        mreq = make_mreq(sock.family, address)

        # Quit group
        if sock.family == socket.AF_INET:
            # IPv4
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)

        elif sock.family == socket.AF_INET6:
            # IPv6
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_LEAVE_GROUP, mreq)

    # Close the socket
    sock.close()

# ------------------------------------------------------------------------------

@ComponentFactory("pelix-remote-discovery-multicast-factory")
@Provides(pelix.remote.SERVICE_ENDPOINT_LISTENER)
@Requires("_dispatcher", pelix.remote.SERVICE_DISPATCHER)
@Requires('_access', pelix.remote.SERVICE_DISPATCHER_SERVLET)
@Requires("_registry", pelix.remote.SERVICE_REGISTRY)
@Property("_group", "multicast.group", "239.0.0.1")
@Property("_port", "multicast.port", 42000)
@Property("_listener_flag", pelix.remote.PROP_LISTEN_EXPORTED, True)
class MulticastDiscovery(object):
    """
    Remote services discovery and notification using multicast packets
    """
    def __init__(self):
        """
        Sets up the component
        """
        # End point listener flag
        self._listener_flag = True

        # End points registry
        self._dispatcher = None
        self._registry = None

        # Dispatcher access
        self._access = None

        # Framework UID
        self._fw_uid = None

        # Socket
        self._group = "239.0.0.1"
        self._port = 42000
        self._socket = None
        self._target = None

        # Reception loop
        self._stop_event = threading.Event()
        self._thread = None


    def _make_endpoint_dict(self, event, endpoint):
        """
        Converts the end point into an event packet dictionary
        
        :param event: The kind of event: add, update, remove
        :param endpoint: An end point description object
        :return: A dictionary
        """
        # Get the dispatcher servlet access
        access = self._access.get_access()

        # Make the event packet content
        packet = {"sender": self._fw_uid,  # Framework UID
                  "event": event,  # Kind of event
                  "uid": endpoint.uid,  # Endpoint UID
                  "access": {"port": access[0],  # Access to the dispatcher
                             "path": access[1]}  # servlet
                  }

        if event == "update":
            # Give the new end point properties
            packet["new_properties"] = endpoint.reference.get_properties()

        return packet


    def __send_packet(self, data, target=None):
        """
        Sends a UDP datagram to the given target, if given, or to the multicast
        group.
        
        :param data: The content of the datagram
        :param target: The packet target (can be None)
        """
        if target is None:
            # Use the multicast target by default
            target = self._target

        # Converts data to bytes
        data = to_bytes(data)

        # Send the data
        self._socket.sendto(data, 0, target)


    def _send_discovery(self):
        """
        Sends a discovery packet, requesting others to indicate their services
        """
        # Get the dispatcher servlet access
        access = self._access.get_access()

        # Make the discovery packet content
        data = {"event": "discovery",  # Discovery packet
                "sender": self._fw_uid,  # Framework UID
                "access": {"port": access[0],  # Access to the dispatcher
                           "path": access[1]}  # servlet
                }

        # Send a JSON request
        data = json.dumps(data)
        self.__send_packet(data)


    def _send_discovered(self, sender):
        """
        Sends a "discovered" packet to the one that sent a "discovery" packet
        
        :param sender: An (address, port) tuple
        """
        # Get the dispatcher servlet access
        access = self._access.get_access()

        # Make the discovery packet content
        data = {"event": "discovered",  # "Discovered" packet
                "sender": self._fw_uid,  # Framework UID
                "access": {"port": access[0],  # Access to the dispatcher
                           "path": access[1]}  # servlet
                }

        # Send a JSON request
        data = json.dumps(data)
        self.__send_packet(data, sender)


    def endpoint_added(self, endpoint):
        """
        A new service is exported
        """
        # Send a JSON event
        data = json.dumps(self._make_endpoint_dict("add", endpoint))
        self.__send_packet(data)


    def endpoint_updated(self, endpoint, old_properties):
        """
        An end point is updated
        """
        # Send a JSON event
        data = json.dumps(self._make_endpoint_dict("update", endpoint,
                                                   old_properties))
        self.__send_packet(data)


    def endpoint_removed(self, endpoint):
        """
        An end point is removed
        """
        # Send a JSON event
        data = json.dumps(self._make_endpoint_dict("remove", endpoint))
        self.__send_packet(data)


    def _handle_packet(self, sender, raw_data):
        """
        Calls the method associated to the kind of event indicated in the given
        packet.
        
        :param sender: The (address, port) tuple of the client
        :param raw_data: Raw packet content
        """
        # Decode content
        data = json.loads(raw_data)

        # Avoid handling our own packets
        sender_uid = data['sender']
        if sender_uid == self._fw_uid:
            return

        # Dispatch the event
        event = data['event']
        if event == "discovery":
            # Discovery request
            self._send_discovered(sender)

        elif event == "discovered":
            # Answer to a discovery request
            access = data['access']
            endpoints = self.grab_endpoints(sender[0], access['port'],
                                            access['path'])
            if endpoints:
                for endpoint in endpoints:
                    self._register_endpoint(sender[0], endpoint)

        elif event in ('add', 'update', 'remove'):
            # End point event
            self._handle_event_packet(sender, data)

        else:
            _logger.warning("Unknown event '%s' from %s", event, sender)


    def _handle_event_packet(self, sender, data):
        """
        Handles an end point event packet
        
        :param sender: The (address, port) tuple of the client
        :param data: Decoded packet content
        """
        # Get the event
        event = data['event']
        endpoint_uid = data['uid']
        framework_uid = data['sender']

        if event == 'add':
            # Store it
            access = data['access']
            endpoint = self.grab_endpoint(sender[0], access['port'],
                                          access['path'], endpoint_uid)
            if endpoint is not None:
                self._register_endpoint(sender[0], endpoint)

        elif event == 'remove':
            # Remove it
            self._registry.remove(endpoint_uid)

        elif event == 'update':
            # Update it
            new_properties = data['new_properties']
            self.__filter_properties(framework_uid, new_properties)
            self._registry.update(endpoint_uid, new_properties)


    def __filter_properties(self, framework_uid, properties):
        """
        Replaces in-place export properties by import ones
        
        :param framework_uid: The UID of the framework exporting the service
        :param properties: End point properties
        :return: The filtered dictionary.
        """
        # Add the "imported" property
        properties[pelix.remote.PROP_IMPORTED] = True

        # Replace the "exported configs"
        if pelix.remote.PROP_EXPORTED_CONFIGS in properties:
            properties[pelix.remote.PROP_IMPORTED_CONFIGS] = \
                                properties[pelix.remote.PROP_EXPORTED_CONFIGS]

        # Clear export properties
        for name in (pelix.remote.PROP_EXPORTED_CONFIGS,
                     pelix.remote.PROP_EXPORTED_INTERFACES):
            if name in properties:
                del properties[name]

        # Add the framework UID to the properties
        properties[pelix.remote.PROP_FRAMEWORK_UID] = framework_uid

        return properties


    def _register_endpoint(self, host_address, endpoint_dict):
        """
        Registers a new end point in the registry
        
        :param host_address: Address of the service exporter
        :param endpoint_dict: An end point description dictionary (result of 
                              a request to the dispatcher servlet)
        """
        # Filter properties
        properties = self.__filter_properties(endpoint_dict['sender'],
                                              endpoint_dict['properties'])

        # Format the URL
        url = endpoint_dict['url'].format(server=host_address)

        # Create the end point object
        endpoint = pelix.remote.ImportEndpoint(endpoint_dict['uid'],
                                               endpoint_dict['kind'],
                                               endpoint_dict['name'],
                                               url,
                                               endpoint_dict['specifications'],
                                               properties)

        # Register it
        self._registry.add(endpoint)


    def grab_endpoint(self, host, port, path, uid):
        """
        Retrieves the description of the end point with the given UID at the
        given dispatcher servlet.
        Returns the end point description as a dictionary, or None in case of
        error.
        Does not register nor converts the end point.
        
        :param host: Dispatcher host address
        :param port: Dispatcher HTTP service port
        :param path: Path to the dispatcher servlet
        :param uid: The UID of an end point
        :return: An end point dictionary or None
        """
        # Setup the request URI
        if path[-1] == '/':
            path = path[:-1]

        request_path = "{0}/endpoint/{1}".format(path, uid)

        return self.__grab_data(host, port, request_path)


    def grab_endpoints(self, host, port, path):
        """
        Retrieves all end points available in the dispatcher servlet at the
        given path.
        Returns the result of the dispatcher servlet (list of dictionaries), or
        None in case of error.
        Does not register nor converts the end points.

        :param host: Dispatcher host address
        :param port: Dispatcher HTTP service port
        :param path: Path to the dispatcher servlet
        :return: A list of dictionaries or None
        """
        # Setup the request URI
        if path[-1] == '/':
            path = path[:-1]

        request_path = "{0}/endpoints".format(path)

        return self.__grab_data(host, port, request_path)


    def __grab_data(self, host, port, path):
        """
        Sends a HTTP request to the server at (host, port), on the given path.
        Returns the parsed response.
        Returns None if the HTTP result is not 200 or in case of error.

        :param host: Dispatcher host address
        :param port: Dispatcher HTTP service port
        :param path: Request path
        :return: The parsed response content, or None
        """
        # Request the end points
        try:
            conn = httplib.HTTPConnection(host, port)
            conn.request("GET", path)
            result = conn.getresponse()
            data = result.read()
            conn.close()

        except Exception as ex:
            _logger.exception("Error accessing the dispatcher servlet: %s", ex)
            return

        if result.status != 200:
            # Not a valid result
            return

        try:
            # Parse the JSON result
            return json.loads(data)

        except ValueError as ex:
            # Error parsing data
            _logger.error("Error reading the response of the dispatcher: %s",
                          ex)


    def _read_loop(self):
        """
        Reads packets from the socket
        """
        while not self._stop_event.is_set():
            # Watch for content
            ready = select.select([self._socket], [], [], 1)
            if ready[0]:
                # Socket is ready
                data, sender = self._socket.recvfrom(1024)
                try:
                    data = to_str(data)
                    self._handle_packet(sender, data)

                except Exception as ex:
                    _logger.exception("Error handling the packet: %s", ex)


    @Invalidate
    def invalidate(self, context):
        """
        Component invalidated
        """
        # Stop the loop
        self._stop_event.set()

        # Join the thread
        self._thread.join()

        # Close the socket
        close_multicast_socket(self._socket, self._target[0])

        # Clean up
        self._thread = None
        self._socket = None
        self._target = None
        self._fw_uid = None

        _logger.debug("Multicast discovery invalidated")


    @Validate
    def validate(self, context):
        """
        Component validated
        """
        # Ensure we have a valid port
        self._port = int(self._port)

        # Get the framework UID
        self._fw_uid = context.get_property(pelix.framework.FRAMEWORK_UID)

        # Create the socket
        self._socket, address = create_multicast_socket(self._group, self._port)

        # Store group access information
        self._target = (address, self._port)

        # Start the listening thread
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._read_loop)
        self._thread.start()

        # Send a discovery request
        self._send_discovery()

        _logger.debug("Multicast discovery validated: group=%s port=%d",
                      self._group, self._port)
