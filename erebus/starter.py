"""
"""
import logging
import os
import sys
import time

import erebus.util.arguments
import erebus.util.controller
import erebus.webapp

from twisted.internet import reactor
from stem.util import conf, log

from erebus.server import websockets
from erebus.util import uses_settings, dual_mode, set_dual_mode, msg

CONFIG = conf.config_dict('erebus', {
    'server.address': '127.0.0.1',
    'server.port': 8887,
    'client.port': 8889,
})


@uses_settings
def main(config):
    config.set('start_time', str(int(time.time())))

    try:
        args = erebus.util.arguments.parse(sys.argv[1:])
        config.set('startup.events', args.logged_events)
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    if args.print_help:
        print(erebus.util.arguments.get_help())
        sys.exit()
    elif args.print_version:
        print(erebus.util.arguments.get_version())
        sys.exit()

    if args.debug_path is not None:
        try:
            _setup_debug_logging(args)
            print(msg('debug.saving_to_path', path=args.debug_path))
        except IOError as exc:
            print(msg(
                'debug.unable_to_write_file',
                path=args.debug_path,
                error=exc.strerror
            ))
            sys.exit(1)

    control_port = (args.control_address, args.control_port)
    control_socket = args.control_socket

    # If the user specified an endpoint then just try to connect to that.
    if args.user_provided_socket and not args.user_provided_port:
        control_port = None
    elif args.user_provided_port and not args.user_provided_socket:
        control_socket = None

    # Check if user wants to run erebus in dual mode (both server and
    # client in the same port. If that is the case, activate dual mode
    # and make server as primary option to run (since server would
    # import client functionality)
    run_server = True
    if args.dual_mode:
        set_dual_mode()
    else:
        # If the user specified client mode.
        if args.client_mode and not args.server_mode:
            run_server = False
        elif args.client_mode and args.server_mode:
            set_dual_mode()
        # In any other case, server mode is default

    if run_server:
        # Init empty list of websockets and start logging erebus events
        ws_controller = websockets.init_websockets()
        ws_controller.listen_erebus_log(erebus.util.arguments.expand_events(config.get('startup.events')))
        # Init erebus controller (and Tor controller, if connected)
        erebus.util.controller.init_controller(
            control_port,
            control_socket,
            config.get('startup.events'),
        )
        # server app
        app = erebus.webapp.Application()
        # Check if user specified a server port
        if args.user_provided_server_port:
            config.set('server.port', str(args.server_port))
        listen_port = CONFIG['server.port']

        if dual_mode():
            log.debug('Running in dual mode')
        else:
            log.debug('Running in server mode')
    else:
        # client app
        app = erebus.webapp.Application(True)
        # Check if user specified listen (client) port
        if args.user_provided_listen_port:
            config.set('client.port', str(args.listen_port))
        listen_port = CONFIG['client.port']

        log.debug('Running in client mode')

    # This is where we are going to connect for fetching data
    # (different from listen port, where the app will run)
    if args.user_provided_server_port:
        config.set('server.port', str(args.server_port))
    if args.user_provided_server_address:
        config.set('server.address', args.server_address)

    server_port = CONFIG['server.port']
    server_address = CONFIG['server.address']

    log.debug('Erebus is running on port %s' % listen_port)
    log.debug('Erebus server is located at: %s:%s' % (server_address,
                                                    server_port))

    reactor.listenTCP(listen_port, app)
    reactor.run()


def _setup_debug_logging(args):
    """
    Configures us to log at stem's trace level to a debug log path.
    This starts it off with some general diagnostic information.
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


if __name__ == '__main__':
    main()
