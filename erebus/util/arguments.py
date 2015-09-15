"""
Commandline argument parsing for erebus.
"""

import collections
import getopt
import os

import stem.util.connection

import erebus

from erebus.server.handlers.log import TOR_EVENT_TYPES
from erebus.util import msg

DEFAULT_ARGS = {
    'server_address': None,
    'user_provided_server_address': False,
    'server_port': None,
    'user_provided_server_port': False,
    'listen_port': None,
    'user_provided_listen_port': False,
    'server_mode': False,
    'client_mode': False,
    'dual_mode': False,
    'control_address': '127.0.0.1',
    'control_port': 9051,
    'user_provided_port': False,
    'control_socket': '/var/run/tor/control',
    'user_provided_socket': False,
    'config': os.path.expanduser('./erebus/config/erebusrc'),
    'debug_path': None,
    'logged_events': 'N3',
    'print_version': False,
    'print_help': False,
}

OPT = 'a:p:l:i:S:C:D:L:scdvh'

OPT_EXPANDED = [
    'address=',
    'port=',
    'listen-port=',
    'interface=',
    'socket=',
    'config=',
    'debug=',
    'log=',
    'server',
    'client',
    'dual',
    'version',
    'help',
]


def parse(argv):
    """
    Parses our arguments, providing a named tuple with their values.

    :param list argv: input arguments to be parsed

    :returns: a **named tuple** with our parsed arguments

    :raises: **ValueError** if we got an invalid argument
    """

    args = dict(DEFAULT_ARGS)

    try:
        recognized_args, unrecognized_args = getopt.getopt(argv, OPT, OPT_EXPANDED)
        if unrecognized_args:
            error_msg = "aren't recognized arguments" if len(unrecognized_args) > 1 else "isn't a recognized argument"
            raise getopt.GetoptError("'%s' %s" % ("', '".join(unrecognized_args), error_msg))
    except getopt.GetoptError as exc:
        raise ValueError(msg('usage.invalid_arguments', error=exc))

    for opt, arg in recognized_args:
        if opt in ('-a', '--address'):
            if not stem.util.connection.is_valid_ipv4_address(arg):
                raise ValueError(msg('usage.not_a_valid_address', address_input=arg))

            args['server_address'] = arg
            args['user_provided_server_address'] = True
        elif opt in ('-p', '--port'):
            if not stem.util.connection.is_valid_port(arg):
                raise ValueError(msg('usage.not_a_valid_port', port_input=arg))

            args['server_port'] = int(arg)
            args['user_provided_server_port'] = True
        elif opt in ('-l', '--listen-port'):
            if not stem.util.connection.is_valid_port(arg):
                raise ValueError(msg('usage.not_a_valid_port', port_input=arg))

            args['listen_port'] = int(arg)
            args['user_provided_listen_port'] = True
        elif opt in ('-i', '--interface'):
            if ':' in arg:
                address, port = arg.split(':', 1)
            else:
                address, port = None, arg

            if address is not None:
                if not stem.util.connection.is_valid_ipv4_address(address):
                    raise ValueError(msg('usage.not_a_valid_address', address_input=address))

                args['control_address'] = address

            if not stem.util.connection.is_valid_port(port):
                raise ValueError(msg('usage.not_a_valid_port', port_input=port))

            args['control_port'] = int(port)
            args['user_provided_port'] = True
        elif opt in ('-S', '--socket'):
            args['control_socket'] = arg
            args['user_provided_socket'] = True
        elif opt in ('-C', '--config'):
            args['config'] = arg
        elif opt in ('-D', '--debug'):
            args['debug_path'] = os.path.expanduser(arg)
        elif opt in ('-L', '--log'):
            try:
                expand_events(arg)
            except ValueError as exc:
                raise ValueError(msg('usage.unrecognized_log_flags', flags=exc))

            args['logged_events'] = arg
        elif opt in ('-s', '--server'):
            args['server_mode'] = True
        elif opt in ('-c', '--client'):
            args['client_mode'] = True
        elif opt in ('-d', '--dual'):
            args['dual_mode'] = True
        elif opt in ('-v', '--version'):
            args['print_version'] = True
        elif opt in ('-h', '--help'):
            args['print_help'] = True

    # translates our args dict into a named tuple
    Args = collections.namedtuple('Args', args.keys())
    return Args(**args)


def get_help():
    """
    Provides our --help usage information.

    :returns: **str** with our usage information
    """

    return msg(
        'usage.help_output',
        address=DEFAULT_ARGS['control_address'],
        port=DEFAULT_ARGS['control_port'],
        socket=DEFAULT_ARGS['control_socket'],
        config_path=DEFAULT_ARGS['config'],
        events=DEFAULT_ARGS['logged_events'],
        event_flags=msg('misc.event_types'),
    )


def get_version():
    """
    Provides our --version information.

    :returns: **str** with our versioning information
    """

    return msg(
        'usage.version_output',
        version=erebus.__version__,
        date=erebus.__release_date__,
    )


def expand_events(flags):
    """
    Expands event abbreviations to their full names. Beside mappings
    provided in TOR_EVENT_TYPES this recognizes the following special
    events and aliases:

    * A - all events
    * X - no events
    * U - UKNOWN events
    * DINWE - runlevel and higher
    * 12345 - erebus/stem runlevel and higher (EREBUS_DEBUG - EREBUS_ERR)

    For example...

    ::

    >>> expand_events('inUt')
    set(['INFO', 'NOTICE', 'UNKNOWN', 'STATUS_CLIENT'])

    >>> expand_events('N4')
    set(['NOTICE', 'WARN', 'ERR', 'EREBUS_WARN', 'EREBUS_ERR'])

    >>> expand_events('cfX')
    set([])

    :param str flags: character flags to be expanded

    :returns: **set** of the expanded event types

    :raises: **ValueError** with invalid input if any flags are unrecognized
    """

    expanded_events, invalid_flags = set(), ''

    tor_runlevels = ['DEBUG', 'INFO', 'NOTICE', 'WARN', 'ERR']
    erebus_runlevels = ['EREBUS_' + runlevel for runlevel in tor_runlevels]

    for flag in flags:
        if flag == 'A':
            return set(list(TOR_EVENT_TYPES) + erebus_runlevels + ['UNKNOWN'])
        elif flag == 'X':
            return set()
        elif flag in 'DINWE12345':
            # all events for a runlevel and higher

            if flag in 'D1':
                runlevel_index = 0
            elif flag in 'I2':
                runlevel_index = 1
            elif flag in 'N3':
                runlevel_index = 2
            elif flag in 'W4':
                runlevel_index = 3
            elif flag in 'E5':
                runlevel_index = 4

            if flag in 'DINWE':
                runlevels = tor_runlevels[runlevel_index:]
            elif flag in '12345':
                runlevels = erebus_runlevels[runlevel_index:]

            expanded_events.update(set(runlevels))
        elif flag == 'U':
            expanded_events.add('UNKNOWN')
        elif flag in TOR_EVENT_TYPES:
            expanded_events.add(TOR_EVENT_TYPES[flag])
        else:
            invalid_flags += flag

    if invalid_flags:
        raise ValueError(''.join(set(invalid_flags)))
    else:
        return expanded_events
