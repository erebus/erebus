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
Handler for erebus controller, which is in charge of starting a tor
control connection if tor is up, or wait and retry periodically to connect
again.
"""

import stem

from twisted.internet import task

from stem.control import State, EventType
from stem.util import conf, log

from erebus.server.handlers.graph import init_bw_handler
from erebus.server import websockets
from erebus.util import msg, init_tor_controller, tor_controller, uses_settings


def conf_handler(key, value):
    if key == 'conn.loopInterval':
        return max(15, value)

CONFIG = conf.config_dict('erebus', {
    'conn.loopInterval': 10,
}, conf_handler)

EREBUS_CONTROLLER = None


def erebus_controller():
    """
    Provides the EREBUS_CONTROLLER singleton.

    :returns: :class:`~erebus.util.controller.Controller`
    """

    return EREBUS_CONTROLLER


def init_controller(control_port, control_socket):
    """
    Initializes the erebus controller instance.

    :param tuple control_port: tuple of the form (address, port)
    :param str control_socket: string with path to control socket.
    """

    global EREBUS_CONTROLLER
    EREBUS_CONTROLLER = Controller(control_port, control_socket)


class Controller:
    """
    Tracks the state of the connection to tor control.
    """

    def __init__(self, control_port, control_socket):
        """
        Sets default values and starts a loop task to connect to tor control.

        :var tuple _control_port: tuple of the form (address, port)
        :var str _control_socket: string with path to control socket.
        """

        self._loop_call = None
        self._control_port = control_port
        self._control_socket = control_socket

        self._start_loop_check()

    @uses_settings
    def _start_loop_check(self, config):
        """
        Starts a looping task to periodically check for tor control
        connection.
        """

        if self._loop_call is None:
            self._loop_call = task.LoopingCall(self._conn_starter)
        try:
            # The loop task repeats itself every `loopInterval` seconds.
            self._loop_call.start(CONFIG['conn.loopInterval'])
        except AssertionError as exc:
            log.warn(msg('setup.already_looping', detail=exc))

    def _conn_starter(self):
        """
        Function to be called from the looping task at _start_loop_check()
        If a connection is made, then stop the looping task.
        """

        controller = tor_controller()
        if controller is None or not controller.is_alive():
            self._start_tor_controller()
            log.notice(msg(
                'notice.try_to_connect', interval=CONFIG['conn.loopInterval']))
        else:
            self._loop_call.stop()

    def _conn_listener(self, controller, state, timestamp):
        """
        Function to be called when tor control connection changes its
        state. If the new state is CLOSED, then try to reconnect.

        :param Class controller: :class:`~stem.control.BaseController`.
        :param Class state: :class:`~stem.control.State` enumeration for
          states that a controller can have.
        :param float timestamp: Unix timestamp.
        """

        if state == State.CLOSED:
            log.notice(msg('notice.control_conn_closed'))
            self._start_loop_check()

    def _start_tor_controller(self):
        """
        Starts a new connection with tor control.
        """

        controller = init_tor_controller(
            control_port=self._control_port,
            control_socket=self._control_socket
        )

        if controller is not None:
            log.notice(msg('notice.new_connection'))

            # If the connection to tor control is made, then start
            # logging tor events.
            ws_controller = websockets.ws_controller()
            ws_controller.listen_tor_log()
            # Setup the handler to start listening for bandwidth events
            init_bw_handler()

            try:
                # Bandwidth events
                controller.add_event_listener(
                    ws_controller.bw_event, EventType.BW)
                # Tor control connection state
                controller.add_status_listener(ws_controller.reset_listener)
                controller.add_status_listener(self._conn_listener)
                # Once everything is OK, send useful relay information
                # to the client.
                ws_controller.startup_info()

            except stem.ProtocolError as exc:
                log.warn(msg('warn.unable_to_attach', reason=exc))
