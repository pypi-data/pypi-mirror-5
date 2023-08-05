#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Pelix shell bundle.

Provides the basic command parsing and execution support to make a Pelix shell.

:author: Thomas Calmant
:copyright: Copyright 2013, isandlaTech
:license: GPLv3
:version: 0.2
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
__version_info__ = (0, 2, 0)
__version__ = ".".join(map(str, __version_info__))

# Documentation strings format
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------

# Shell constants
from pelix.shell import SHELL_SERVICE_SPEC, SHELL_COMMAND_SPEC, \
    SHELL_UTILS_SERVICE_SPEC

# Pelix modules
from pelix.utilities import to_str
import pelix.framework as pelix

# Standard library
import io
import logging
import os
import shlex
import sys
import traceback

# ------------------------------------------------------------------------------

DEFAULT_NAMESPACE = "default"
""" Default command name space: default """

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------

def _find_assignment(arg_token):
    """
    Find the first non-escaped assignment in the given argument token.
    Returns -1 if no assignment was found.

    :param arg_token: The argument token
    :return: The index of the first assignment, or -1
    """
    idx = arg_token.find('=')
    while idx != -1:
        if idx != 0:
            if arg_token[idx - 1] != '\\':
                # No escape character
                return idx

        idx = arg_token.find('=', idx + 1)

    # No assignment found
    return -1


def _make_args(args_list):
    """
    Converts the given list of arguments into a list (args) and a
    dictionary (kwargs).
    All arguments with an assignment are put into kwargs, others in args.

    :param args_list: The list of arguments to be treated
    :return: The (arg_token, kwargs) tuple.
    """
    args = []
    kwargs = {}

    for arg_token in args_list:
        idx = _find_assignment(arg_token)
        if idx != -1:
            # Assignment
            key = arg_token[:idx]
            value = arg_token[idx + 1:]
            kwargs[key] = value

        else:
            # Direct argument
            args.append(arg_token)

    return args, kwargs


def _split_ns_command(cmd_token):
    """
    Extracts the name space and the command name of the given command token

    :param cmd_token: The command token
    :return: The extracted (name space, command) tuple
    """
    namespace = None
    cmd_split = cmd_token.split('.', 1)
    if len(cmd_split) == 1:
        # No name space given
        command = cmd_split[0]

    else:
        # Got a name space and a command
        namespace = cmd_split[0]
        command = cmd_split[1]

    if not namespace:
        # No name space given or empty one
        namespace = DEFAULT_NAMESPACE

    # Use lower case values only
    return namespace.lower(), command.lower()

# ------------------------------------------------------------------------------

class IOHandler(io.RawIOBase):
    """
    Handles I/O operations between the command handler and the client
    It automatically converts the given data to bytes in Python 3.
    """
    def __init__(self, instream, out_stream, encoding='UTF-8'):
        """
        Sets up the printer
        
        :param instream: Input stream
        :param out_stream: Output stream
        :param encoding: Output encoding
        """
        self.input = instream
        self.output = out_stream
        self.encoding = encoding

        # Set up class methods
        if sys.version_info[0] == 3:
            self.read = self._read_python3
            self.write = self._write_python3

        else:
            self.read = self.input.read
            self.write = self.output.write


    def _read_python3(self, n):
        """
        Reads the input stream
        
        :param n: Maximum bytes to read
        :return: The result of ``self.input.read()``
        """
        return to_str(self.input.read(n), self.encoding)


    def _write_python3(self, data):
        """
        Converts the given data then writes it
        
        :param data: Data to be written
        :return: The result of ``self.output.write()``
        """
        self.output.write(to_str(data, self.encoding))


    def write_line(self, line, *args, **kwargs):
        """
        Formats and writes a line to the output
        """
        if line is None:
            # Empty line
            line = '\n'

        else:
            # Format the line
            line = line.format(*args, **kwargs)

        # Add the trailing new line
        if line[-1] != '\n':
            line = line + '\n'

        # Write it
        self.write(line)


# ------------------------------------------------------------------------------

class ShellUtils(object):
    """
    Utility methods for the shell
    """
    def bundlestate_to_str(self, state):
        """
        Converts a bundle state integer to a string
        """
        states = {
                  pelix.Bundle.INSTALLED:   "INSTALLED",
                  pelix.Bundle.ACTIVE:      "ACTIVE",
                  pelix.Bundle.RESOLVED:    "RESOLVED",
                  pelix.Bundle.STARTING:    "STARTING",
                  pelix.Bundle.STOPPING:    "STOPPING",
                  pelix.Bundle.UNINSTALLED: "UNINSTALLED"
        }

        return states.get(state, "Unknown state (%d)".format(state))


    def make_table(self, headers, lines):
        """
        Generates an ASCII table according to the given headers and lines

        :param headers: List of table headers (N-tuple)
        :param lines: List of table lines (N-tuples).
        :return: The ASCII representation of the table
        :raise ValueError: Different number of columns between headers and lines
        """
        if lines and len(headers) != len(lines[0]):
            raise ValueError("Different sizes for header and lines")

        # Maximum lengths
        lengths = [len(title) for title in headers]

        # Lines
        str_lines = []
        for line in lines:
            # Recompute lengths
            i = 0
            str_line = []
            str_lines.append(str_line)
            for entry in line:
                str_entry = str(entry)
                str_line.append(str_entry)

                if len(str_entry) > lengths[i]:
                    lengths[i] = len(str_entry)
                i += 1

        # Prepare the head (centered text)
        format_str = "|"
        i = 0
        for length in lengths:
            format_str += " {%d:^%d} |" % (i, length)
            i += 1

        head_str = format_str.format(*headers)

        # Prepare the separator, according the length of the headers string
        separator = '-' * len(head_str)
        idx = head_str.find('|')
        while idx != -1:
            separator = '+'.join((separator[:idx], separator[idx + 1:]))
            idx = head_str.find('|', idx + 1)

        # Prepare the output
        output = []
        output.append(separator)
        output.append(head_str)
        output.append(separator.replace('-', '='))

        # Compute the lines
        format_str = format_str.replace('^', '<')
        for line in str_lines:
            output.append(format_str.format(*line))
            output.append(separator)

        # Force the last end of line
        output.append("")

        # Join'em
        return '\n'.join(output)

# ------------------------------------------------------------------------------

class Shell(object):
    """
    A simple shell, based on shlex.

    Allows to use name spaces.
    """
    def __init__(self, context, utilities):
        """
        Sets up the shell

        :param context: The bundle context
        """
        self._commands = {}
        self._context = context
        self._utils = utilities

        # Bound services: reference -> service
        self._bound_references = {}

        # Service reference -> (name space, [commands])
        self._reference_commands = {}

        # Register basic commands
        self.register_command(None, "bd", self.bundle_details)
        self.register_command(None, "bl", self.bundles_list)

        self.register_command(None, "sd", self.service_details)
        self.register_command(None, "sl", self.services_list)

        self.register_command(None, "start", self.start)
        self.register_command(None, "stop", self.stop)
        self.register_command(None, "update", self.update)
        self.register_command(None, "install", self.install)
        self.register_command(None, "uninstall", self.uninstall)

        self.register_command(None, "properties", self.properties_list)
        self.register_command(None, "property", self.property_value)

        self.register_command(None, "sysprops", self.environment_list)
        self.register_command(None, "sysprop", self.environment_value)

        self.register_command(None, "threads", self.threads_list)
        self.register_command(None, "thread", self.thread_details)

        self.register_command(None, "help", self.print_help)
        self.register_command(None, "?", self.print_help)

        self.register_command(None, "quit", self.quit)
        self.register_command(None, "close", self.quit)
        self.register_command(None, "exit", self.quit)


    def _bind_handler(self, svc_ref):
        """
        Called if a command service has been found.
        Registers the methods of this service.
        
        :param svc_ref: A reference to the found service
        :return: True if the commands have been registered
        """
        if svc_ref in self._bound_references:
            # Already bound service
            return False

        # Get the service
        handler = self._context.get_service(svc_ref)

        # Get its name space
        namespace = handler.get_namespace()
        commands = []

        # Get the host exporting the service, if any
        remote_host = None
        if svc_ref.get_property("service.imported"):
            # Imported service: store its host
            remote_host = svc_ref.get_property("service.imported.from")

        if not remote_host:
            # Local service: register all its methods directly
            for command, method in handler.get_methods():
                self.register_command(namespace, command, method)
                commands.append(command)

        else:
            # Imported service
            _logger.info("Bound to a remote command handler from %s",
                         remote_host)

            # Prefix its name space
            namespace = ".".join((remote_host, namespace))
            for command, method_name in handler.get_methods_names():
                # Use a proxy to call the methods
                def proxy(*args, **kwargs):
                    """
                    Remote command proxy
                    """
                    return getattr(handler, method_name)(*args, **kwargs)

                self.register_command(namespace, command, proxy)
                commands.append(command)

        # Store the reference
        self._bound_references[svc_ref] = handler
        self._reference_commands[svc_ref] = (namespace, commands)
        return True


    def _unbind_handler(self, svc_ref):
        """
        Called if a command service is gone.
        Unregisters its commands.
        
        :param svc_ref: A reference to the unbound service
        :return: True if the commands have been unregistered
        """
        if svc_ref not in self._bound_references:
            # Unknown reference
            return False

        # Unregister its commands
        namespace, commands = self._reference_commands[svc_ref]
        for command in commands:
            self.unregister(namespace, command)

        # Release the service
        self._context.unget_service(svc_ref)
        del self._bound_references[svc_ref]
        del self._reference_commands[svc_ref]
        return True


    def register_command(self, namespace, command, method):
        """
        Registers the given command to the shell.

        The namespace can be None, empty or "default"

        :param namespace: The command name space.
        :param command: The shell name of the command
        :param method: The method to call
        :return: True if the method has been registered, False if it was already
                 known or invalid
        """
        if not namespace:
            namespace = DEFAULT_NAMESPACE

        if not command:
            _logger.error("No command name given")
            return False

        if method is None:
            _logger.error("No method given for %s.%s", namespace, command)
            return False

        # Store everything in lower case
        namespace = namespace.lower()
        command = command.lower()

        if namespace not in self._commands:
            space = self._commands[namespace] = {}
        else:
            space = self._commands[namespace]

        if command in space:
            _logger.error("Command already registered: %s.%s", namespace,
                          command)
            return False

        space[command] = method
        return True


    def unregister(self, namespace, command=None):
        """
        Unregisters the given command. If command is None, the whole name space
        is unregistered.

        :param namespace: The command name space.
        :param command: The shell name of the command, or None
        :return: True if the command was known, else False
        """
        if not namespace:
            namespace = DEFAULT_NAMESPACE

        namespace = namespace.lower()

        if namespace not in self._commands:
            _logger.warning("Unknown name space: %s", namespace)
            return False

        if command is not None:
            # Remove the command
            if command not in self._commands[namespace]:
                _logger.warning("Unknown command: %s.%s", namespace, command)
                return False

            del self._commands[namespace][command]

            # Remove the name space if necessary
            if not self._commands[namespace]:
                del self._commands[namespace]

        else:
            # Remove the whole name space
            del self._commands[namespace]

        return True


    def execute(self, cmdline, stdin=sys.stdin, stdout=sys.stdout):
        """
        Executes the command corresponding to the given line
        """
        # Split the command line
        if not cmdline:
            return False

        # Convert the line into a string
        cmdline = to_str(cmdline)

        line_split = shlex.split(cmdline, True, True)
        if not line_split:
            return False

        namespace, command = _split_ns_command(line_split[0])

        # Prepare the I/O handler
        io_handler = IOHandler(stdin, stdout)

        # Get the space
        space = self._commands.get(namespace, None)
        if not space:
            _logger.warning("Unknown name space: %s", namespace)
            io_handler.write_line("Unknown name space {0}", namespace)
            return False

        # Get the method
        method = space.get(command, None)
        if method is None:
            _logger.warning("Unknown command: %s.%s", namespace, command)
            io_handler.write_line("Unknown command: {0}.{1}", namespace,
                                  command)
            return False

        # Make arguments and keyword arguments
        args, kwargs = _make_args(line_split[1:])

        # Execute it
        try:
            return method(io_handler, *args, **kwargs)

        except TypeError as ex:
            # Invalid arguments...
            _logger.error("Invalid method call: %s", ex)
            io_handler.write_line("Invalid method call: {0}", ex)
            return False

        except Exception as ex:
            # Error
            io_handler.write_line("{0}: {1}", type(ex).__name__, str(ex))
            return False


    def get_banner(self):
        """
        Returns the Shell banner
        """
        return "** Pelix Shell prompt **"


    def get_ps1(self):
        """
        Returns the PS1, the basic shell prompt
        """
        return "$ "


    def get_namespaces(self):
        """
        Retrieves the list of known name spaces (without the default one)
        
        :return: The list of known name spaces
        """
        namespaces = list(self._commands.keys())
        namespaces.remove(DEFAULT_NAMESPACE)
        namespaces.sort()
        return namespaces


    def get_commands(self, namespace):
        """
        Retrieves the commands of the given name space. If *namespace* is None
        or empty, it retrieves the commands of the default name space
        
        :param namespace: The commands name space
        :return: A list of commands names
        """
        if not namespace:
            # Default namespace:
            namespace = DEFAULT_NAMESPACE

        commands = list(self._commands[namespace].keys())
        commands.sort()
        return commands


    def bundle_details(self, io_handler, bundle_id):
        """
        Prints the details of the given bundle
        """
        try:
            bundle_id = int(bundle_id)
            bundle = self._context.get_bundle(bundle_id)

        except pelix.BundleException:
            io_handler.write_line("Unknown bundle ID: {0}", bundle_id)
            return

        lines = []
        lines.append("ID      : {0}".format(bundle.get_bundle_id()))
        lines.append("Name    : {0}".format(bundle.get_symbolic_name()))
        lines.append("Version : {0}".format(bundle.get_version()))
        lines.append("State   : {0}".format(self._utils.bundlestate_to_str(
                                                        bundle.get_state())))
        lines.append("Location: {0}".format(bundle.get_location()))
        lines.append("Published services:")
        try:
            services = bundle.get_registered_services()
            if services:
                for svc_ref in services:
                    lines.append("\t{0}".format(svc_ref))

            else:
                lines.append("\tn/a")

        except pelix.BundleException as ex:
            # Bundle in a invalid state
            lines.append("\tError: {0}".format(ex))

        lines.append("Services used by this bundle:")
        try:
            services = bundle.get_services_in_use()
            if services:
                for svc_ref in services:
                    lines.append("\t{0}".format(svc_ref))

            else:
                lines.append("\tn/a")

        except pelix.BundleException as ex:
            # Bundle in a invalid state
            lines.append("\tError: {0}".format(ex))

        lines.append("")
        io_handler.write('\n'.join(lines))


    def bundles_list(self, io_handler):
        """
        Lists the bundles in the framework and their state
        """
        # Head of the table
        headers = ('ID', 'Name', 'State', 'Version')

        # Get the bundles
        bundles = self._context.get_bundles()

        # The framework is not in the result of get_bundles()
        bundles.insert(0, self._context.get_bundle(0))

        # Make the entries
        lines = []
        for bundle in bundles:
            # Make the line
            line = [str(entry) for entry in
                    (bundle.get_bundle_id(), bundle.get_symbolic_name(),
                    self._utils.bundlestate_to_str(bundle.get_state()),
                    bundle.get_version())]

            lines.append(line)

        # Print'em all
        io_handler.write(self._utils.make_table(headers, lines))


    def service_details(self, io_handler, service_id):
        """
        Prints the details of the given service
        """
        svc_ref = self._context.get_service_reference(None,
                                '({0}={1})'.format(pelix.SERVICE_ID,
                                                   service_id))
        if svc_ref is None:
            io_handler.write_line('Service not found: {0}', service_id)
            return

        lines = []
        lines.append("ID    : {0}".format(svc_ref.get_property(
                                            pelix.SERVICE_ID)))
        lines.append("Rank  : {0}".format(svc_ref.get_property(
                                            pelix.SERVICE_RANKING)))
        lines.append("Specs : {0}".format(svc_ref.get_property(
                                            pelix.OBJECTCLASS)))
        lines.append("Bundle: {0}".format(svc_ref.get_bundle()))
        lines.append("Properties:")
        for key, value in svc_ref.get_properties().items():
            lines.append("\t{0} = {1}".format(key, value))

        lines.append("Bundles using this service:")
        for bundle in svc_ref.get_using_bundles():
            lines.append("\t{0}".format(bundle))

        lines.append("")
        io_handler.write('\n'.join(lines))


    def services_list(self, io_handler):
        """
        Lists the services in the framework
        """
        # Head of the table
        headers = ('ID', 'Specifications', 'Bundle', 'Ranking')

        # Lines
        references = self._context.get_all_service_references(None, None)

        # Use the reverse order (ascending service IDs instead of descending)
        references.reverse()

        lines = []
        for ref in references:
            # Make the line
            line = [str(entry) for entry in
                    (ref.get_property(pelix.SERVICE_ID),
                     ref.get_property(pelix.OBJECTCLASS),
                     ref.get_bundle(),
                     ref.get_property(pelix.SERVICE_RANKING))]

            lines.append(line)

        # Print'em all
        io_handler.write(self._utils.make_table(headers, lines))


    def print_help(self, io_handler):
        """
        Prints the available methods and their documentation
        """
        namespaces = [namespace for namespace in self._commands.keys()]
        namespaces.remove(DEFAULT_NAMESPACE)
        namespaces.sort()
        namespaces.insert(0, DEFAULT_NAMESPACE)

        for namespace in namespaces:
            io_handler.write_line("* Namespace '{0}':", namespace)
            names = [command for command in self._commands[namespace]]
            names.sort()

            for name in names:
                io_handler.write_line("- {0}", name)
                doc = getattr(self._commands[namespace][name], '__doc__', \
                              None) or "(Documentation missing)"
                io_handler.write_line("\t\t{0}", ' '.join(doc.split()))


    def properties_list(self, io_handler):
        """
        Lists the properties of the framework
        """
        # Get the framework
        framework = self._context.get_bundle(0)

        # Head of the table
        headers = ('Property Name', 'Value')

        # Lines
        lines = [item for item in framework.get_properties().items()]

        # Sort lines
        lines.sort()

        # Print the table
        io_handler.write(self._utils.make_table(headers, lines))


    def property_value(self, io_handler, name):
        """
        property <name> - Prints the value of the given property, looking into
        framework properties then environment variables.
        """
        io_handler.write_line(self._context.get_property(name))


    def environment_list(self, io_handler):
        """
        Lists the framework process environment variables
        """
        # Head of the table
        headers = ('Environment Variable', 'Value')

        # Lines
        lines = [item for item in os.environ.items()]

        # Sort lines
        lines.sort()

        # Print the table
        io_handler.write(self._utils.make_table(headers, lines))


    def environment_value(self, io_handler, name):
        """
        sysprop <name> - Prints the value of the given environment variable
        """
        io_handler.write_line(os.getenv(name))


    def threads_list(self, io_handler):
        """
        Lists the active threads and their current code line
        """
        # Extract frames
        frames = sys._current_frames()

        # Sort by thread ID
        thread_ids = frames.keys()
        thread_ids.sort()

        lines = []
        for thread_id in thread_ids:
            # Get the corresponding stack
            stack = frames[thread_id]

            # Construct the code position
            lines.append('Thread ID: {0}'.format(thread_id))
            lines.append('Stack trace:')
            lines.extend((line.rstrip()
                          for line in traceback.format_stack(stack, 8)))
            lines.append('')

        lines.append('')

        # Sort the lines
        io_handler.write('\n'.join(lines))


    def thread_details(self, io_handler, thread_id):
        """
        thread <id> - Prints details about the given thread
        """
        try:
            stack = sys._current_frames()[int(thread_id)]

        except KeyError:
            io_handler.write_line("Unknown thread ID: {0}", thread_id)

        except ValueError:
            io_handler.write_line("Invalid thread ID: {0}", thread_id)

        else:
            lines = []
            lines.append('Thread ID: {0}'.format(thread_id))
            lines.append('Stack trace:')
            lines.extend((line.rstrip()
                          for line in traceback.format_stack(stack)))

        lines.append("")
        io_handler.write('\n'.join(lines))


    def quit(self, io_handler):
        """
        Stops the current shell session (raises a KeyboardInterrupt exception)
        """
        raise KeyboardInterrupt()


    def start(self, io_handler, bundle_id):
        """
        start <bundle_id> - Starts the given bundle ID
        """
        bundle_id = int(bundle_id)
        bundle = self._context.get_bundle(bundle_id)
        if bundle is None:
            io_handler.write_line("Unknown bundle: {0}", bundle_id)

        bundle.start()


    def stop(self, io_handler, bundle_id):
        """
        stop <bundle_id> - Stops the given bundle
        """
        bundle_id = int(bundle_id)
        bundle = self._context.get_bundle(bundle_id)
        if bundle is None:
            io_handler.write_line("Unknown bundle: {0}", bundle_id)

        bundle.stop()


    def update(self, io_handler, bundle_id):
        """
        update <bundle_id> - Updates the given bundle ID
        """
        bundle_id = int(bundle_id)
        bundle = self._context.get_bundle(bundle_id)
        if bundle is None:
            io_handler.write_line("Unknown bundle: {0}", bundle_id)

        bundle.update()


    def install(self, io_handler, location):
        """
        install <bundle_id> - Installs the given bundle
        """
        bundle = self._context.install_bundle(location)
        io_handler.write_line("Bundle ID: {0}", bundle.get_bundle_id())


    def uninstall(self, io_handler, bundle_id):
        """
        uninstall <bundle_id> - Uninstalls the given bundle
        """
        bundle_id = int(bundle_id)
        bundle = self._context.get_bundle(bundle_id)
        if bundle is None:
            io_handler.write_line("Unknown bundle: {0}", bundle_id)

        bundle.uninstall()


# ------------------------------------------------------------------------------

class PelixActivator(object):
    """
    Activator class for Pelix
    """
    def __init__(self):
        """
        Sets up the activator
        """
        self._shell = None
        self._shell_reg = None
        self._utils_reg = None


    def service_changed(self, event):
        """
        Called when a command provider service event occurred
        """
        kind = event.get_kind()
        reference = event.get_service_reference()

        if kind in (pelix.ServiceEvent.REGISTERED,
                    pelix.ServiceEvent.MODIFIED):
            # New or modified service
            self._shell._bind_handler(reference)

        else:
            # Service gone or not matching anymore
            self._shell._unbind_handler(reference)


    def start(self, context):
        """
        Bundle starting

        :param context: The bundle context
        """
        try:
            # Prepare the shell utility service
            utils = ShellUtils()
            self._shell = Shell(context, utils)

            self._shell_reg = context.register_service(SHELL_SERVICE_SPEC,
                                                       self._shell, {})

            self._utils_reg = context.register_service(SHELL_UTILS_SERVICE_SPEC,
                                                       utils, {})

            # Register the service listener
            spec_filter = '({0}={1})'.format(pelix.OBJECTCLASS,
                                             SHELL_COMMAND_SPEC)
            context.add_service_listener(self, spec_filter)

            # Register existing command services
            refs = context.get_all_service_references(SHELL_COMMAND_SPEC,
                                                      None)
            if refs is not None:
                for ref in refs:
                    self._shell._bind_handler(ref)

            _logger.info("Shell services registered")

        except pelix.BundleException as ex:
            _logger.exception("Error registering the shell service: %s", ex)


    def stop(self, context):
        """
        Bundle stopping

        :param context: The bundle context
        """
        # Unregister the service listener
        context.remove_service_listener(self)

        # Unregister the services
        if self._shell_reg is not None:
            self._shell_reg.unregister()
            self._shell_reg = None

        if self._utils_reg is not None:
            self._utils_reg.unregister()
            self._utils_reg = None

        self._shell = None
        _logger.info("Shell services unregistered")


# Activator for Pelix
activator = PelixActivator()
