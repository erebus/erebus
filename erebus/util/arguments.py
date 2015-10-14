# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Erebus, a web dashboard for tor relays.
#
# :copyright:   (c) 2015, The Tor Project, Inc.
#               (c) 2015, Damian Johnson
#               (c) 2015, Cristobal Leiva
#
# :license: See LICENSE for licensing information.

"""
Commandline argument parsing for erebus (based on nyx's parser).
"""

import collections
import getopt
import os

from stem.util import connection

from erebus import __version__, __release_date__
from erebus.server.handlers.log import TOR_EVENT_TYPES, TOR_RUNLEVELS
from erebus.util import msg


DEFAULT_ARGS = {
    # Args for connecting to erebus server (local or external)
    'server_address': '127.0.0.1',
    'server_port': 8887,

    # Args for tor control connection
    'control_address': '127.0.0.1',
    'control_port': 9051,
    'custom_control_port': False,
    'control_socket': '/var/run/tor/control',
    'custom_control_socket': False,

    # Args for this instance of erebus
    'port': 8889,
    'custom_port': False,
    'config': os.path.expanduser('./erebus/config/erebusrc'),
    'debug_path': None,
    'logged_events': 'N3',
    'erebus_mode': 'D',

    'use_tls': False,
    'print_version': False,
    'print_help': False,
}

OPT = 's:p:m:i:S:c:d:l:tvh'

OPT_EXPANDED = [
    'server=',
    'port=',
    'mode=',
    'interface=',
    'socket=',
    'config=',
    'debug=',
    'log=',
    'tls',
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
        valid_args, invalid_args = getopt.getopt(argv, OPT, OPT_EXPANDED)
        if invalid_args:
            raise getopt.GetoptError(msg(
                'usage.invalid_args', args="', '".join(invalid_args)))
    except getopt.GetoptError as exc:
        raise ValueError(msg('usage.please_use_help', error=exc))

    for opt, arg in valid_args:
        # A valid address and port indicating where to connect to erebus
        # server (in other words, where the client should point when
        # calling for websockets).
        # This arg is of the form: [ADDRESS:]PORT
        if opt in ('-s', '--server'):
            if ':' in arg:
                server_address, server_port = arg.split(':', 1)
            else:
                server_address, server_port = None, arg

            if server_address is not None:
                if not connection.is_valid_ipv4_address(server_address):
                    raise ValueError(msg(
                        'usage.not_a_valid_address', address=server_address))

                args['server_address'] = server_address

            if not connection.is_valid_port(server_port):
                raise ValueError(msg(
                    'usage.not_a_valid_port', port=server_port))

            args['server_port'] = int(server_port)

        # A valid port where this instance of erebus will run, either
        # erebus is running on server or client mode (or both)
        elif opt in ('-p', '--port'):
            if not connection.is_valid_port(arg):
                raise ValueError(msg('usage.not_a_valid_port', port=arg))

            args['port'] = int(arg)
            args['custom_port'] = True

        # Mode in which erebus should run.
        # Valid options are (D)ual, (S)erver, (C)lient.
        elif opt in ('-m', '--mode'):
            if len(arg) == 1 and arg in 'DSC':
                args['erebus_mode'] = arg

        # A valid address and port indicating where to connect to tor control.
        # This arg is of the form: [ADDRESS:]PORT
        elif opt in ('-i', '--interface'):
            if ':' in arg:
                control_address, control_port = arg.split(':', 1)
            else:
                control_address, control_port = None, arg

            if control_address is not None:
                if not connection.is_valid_ipv4_address(control_address):
                    raise ValueError(msg(
                        'usage.not_a_valid_address', address=control_address))

                args['control_address'] = control_address

            if not connection.is_valid_port(control_port):
                raise ValueError(msg(
                    'usage.not_a_valid_port', port=control_port))

            args['control_port'] = int(control_port)
            args['custom_control_port'] = True

        # Unix socket path to connect to tor control.
        # Example: /var/run/tor/control
        elif opt in ('-S', '--socket'):
            args['control_socket'] = arg
            args['custom_control_socket'] = True

        # Path where to look for a config file.
        # Example: ./erebus/config/erebusrc
        elif opt in ('-c', '--config'):
            args['config'] = arg

        # Path where to write erebus logs
        elif opt in ('-d', '--debug'):
            args['debug_path'] = os.path.expanduser(arg)

        # Flags of event types to be logged. See expand_events for further
        # details.
        elif opt in ('-l', '--log'):
            try:
                expand_events(arg)
            except ValueError as exc:
                raise ValueError(msg('usage.invalid_log_flags', flags=exc))

            args['logged_events'] = arg

        # Should we use encrypted HTTP communications
        elif opt in ('-t', '--tls'):
            args['use_tls'] = True
        # Print version and help
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

    :returns: **str** with our versioning information.
    """

    return msg('usage.version', version=__version__, date=__release_date__)


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

    erebus_runlevels = ['EREBUS_' + runlevel for runlevel in TOR_RUNLEVELS]

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
                runlevels = TOR_RUNLEVELS[runlevel_index:]
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
