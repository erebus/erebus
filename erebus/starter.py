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
Parses arguments, starts the web application and connects to tor control
protocol (if tor is up).
"""

import logging
import os
import platform
import stem
import sys
import time

import erebus
import erebus.webapp

from twisted.internet import reactor, ssl
from stem.util import conf, log

from erebus.server import websockets
from erebus.util import arguments, controller
from erebus.util import uses_settings, dual_mode, set_dual_mode, msg

# Default arguments are intended for a local tor instance
CONFIG = conf.config_dict('erebus', {
    'server.address': '127.0.0.1',
    'server.port': 8887,
    'client.port': 8889,
})


@uses_settings
def main(config):
    config.set('start_time', str(int(time.time())))

    try:
        args = arguments.parse(sys.argv[1:])
        config.set('startup.events', args.logged_events)
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    if args.print_help:
        print(arguments.get_help())
        sys.exit()
    elif args.print_version:
        print(arguments.get_version())
        sys.exit()

    if args.debug_path is not None:
        try:
            _setup_debug_logging(args)
            print msg('debug.saving_to_path', path=args.debug_path)
        except IOError as exc:
            print msg(
                'debug.unable_to_write_file', path=args.debug_path,
                error=exc.strerror)
            sys.exit(1)

    control_port = (args.control_address, args.control_port)
    control_socket = args.control_socket

    # If the user specified an endpoint then just try to connect to that.
    if args.custom_control_socket and not args.custom_control_port:
        control_port = None
    elif args.custom_control_port and not args.custom_control_socket:
        control_socket = None

    # Check the mode in which the user wants to run erebus. If the mode
    # is dual, then all of the client functionalities will be imported
    # by the server.
    run_server = True
    if args.erebus_mode == 'D':
        set_dual_mode()
    elif args.erebus_mode == 'C':
        run_server = False

    server_port = args.server_port
    server_address = args.server_address

    if run_server:
        ws_controller = websockets.init_websockets()
        ws_controller.listen_erebus_log(
            arguments.expand_events(config.get('startup.events')))
        # Try to connect to tor instance. If erebus is unable to connect
        # to tor, it will start an asynchronous loop task to retry
        # connecting every X seconds.
        controller.init_controller(control_port, control_socket)

        if args.custom_port:
            server_port = args.port

        # The web app will listen on this port
        listen_port = server_port
        app = erebus.webapp.Application()
    else:
        # The web app will listen on this port
        listen_port = args.port
        app = erebus.webapp.Application(is_client=True)

    # Independently of the port where the web app will run (listen port),
    # we must know to what address:port should erebus connect to fetch
    # info from server.
    config.set('client.port', str(args.port))
    config.set('server.port', str(server_port))
    config.set('server.address', server_address)

    # Useful info
    mode_str = 'dual' if dual_mode() else 'server' if run_server else 'client'
    running_msg = msg('info.running_on', port=listen_port, mode=mode_str)
    server_msg = msg(
        'info.server', protocol='https' if args.use_tls else 'http',
        address=server_address, port=server_port)

    log.info(running_msg)
    log.info(server_msg)

    print running_msg
    print server_msg

    if args.use_tls:
        reactor.listenSSL(
            listen_port, app,
            ssl.DefaultOpenSSLContextFactory(
                # TODO: specify custom files
                'erebus_key.pem', 'erebus_cert.pem'),
            interface=server_address)
    else:
        reactor.listenTCP(listen_port, app)

    config.set('websockets.protocol', 'wss' if args.use_tls else 'ws')

    reactor.run()


def _setup_debug_logging(args):
    """
    Log at stem's trace level to a debug log path.

    :param tuple args: a named tuple with our parsed arguments
    """

    debug_dir = os.path.dirname(args.debug_path)

    if not os.path.exists(debug_dir):
        os.makedirs(debug_dir)

    debug_handler = logging.FileHandler(args.debug_path, mode='w')
    debug_handler.setLevel(log.logging_level(log.TRACE))
    debug_handler.setFormatter(logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S'
    ))

    logger = log.get_logger()
    logger.addHandler(debug_handler)

    erebusrc_content = "[file doesn't exist]"

    if os.path.exists(args.config):
        try:
            with open(args.config) as erebusrc_file:
                erebusrc_content = erebusrc_file.read()
        except IOError as exc:
            erebusrc_content = '[unable to read file: %s]' % exc.strerror

    log.trace(msg(
        'debug.header',
        erebus_version=erebus.__version__,
        stem_version=stem.__version__,
        python_version='.'.join(map(str, sys.version_info[:3])),
        system=platform.system(),
        platform=' '.join(platform.dist()),
        erebusrc_path=args.config,
        erebusrc_content=erebusrc_content,
      ))


if __name__ == '__main__':
    main()
