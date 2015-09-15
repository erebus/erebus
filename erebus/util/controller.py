"""
"""
import stem
import time

from twisted.internet import task

from stem.control import State, EventType
from stem.util import conf, log

from erebus.server.handlers.graph import init_bw_handler
from erebus.server import websockets
from erebus.util import uses_settings, init_tor_controller, tor_controller

EREBUS_CONTROLLER = None


def conf_handler(key, value):
    if key == 'conn.loopInterval':
        return max(15, value)

CONFIG = conf.config_dict('erebus', {
    'startup.events': 'N3',
    'conn.loopInterval': 10,
    'start_time': 0,
}, conf_handler)


def erebus_controller():
    """
    Provides the erebus controller instance.
    """

    return EREBUS_CONTROLLER


def init_controller(control_port, control_socket, logged_events):
    """
    Spawns the controller
    """

    global EREBUS_CONTROLLER
    EREBUS_CONTROLLER = Controller(control_port, control_socket, logged_events)


class Controller:
    """
    Tracks the global state of Erebus controller
    """

    def __init__(self, control_port, control_socket, logged_events):
        """
        Creates a new controller instance. Connect to Tor, setup WebSockets.

        Arguments:
            control_port - tuple with control address and control port
            control_socket - path to control socket
        """

        self._loop_call = None
        self._control_port = control_port
        self._control_socket = control_socket
        self._logged_events = logged_events

        # Try to establish a connection with Tor control
        self._start_loop_check()

    @uses_settings
    def _start_loop_check(self, config):
        """
        Starts a looping task to periodically check for Tor controller
        connection. This looping task should be called when connection to
        Tor controller is off.
        """

        if self._loop_call is None:
            self._loop_call = task.LoopingCall(self._conn_starter)
        try:
            self._loop_call.start(CONFIG['conn.loopInterval'])
        except AssertionError as exc:
            log.warn('The loop check is already running: %s' % exc)

    def _conn_starter(self):
        """
        Looping task to be (periodically) called from self._start_loop_check()
        If the connection is made, stop the looping task.
        """

        controller = tor_controller()
        if controller is None or not controller.is_alive():
            self._start_tor_controller()
        else:
            # Stop the looping task when is started
            self._loop_call.stop()

    def _conn_listener(self, controller, state, timestamp):
        """
        Connection listener. If Tor control is disconnected, then try to
        reconnect.

        Arguments:
        controller, state, timestamp - these are delivered by stem's
        status listener
        """

        if state == State.CLOSED:
            log.notice('Tor control connection closed')
            self._start_loop_check()

    def _start_tor_controller(self):
        """
        Start a new connection with Tor control
        """

        controller = init_tor_controller(
            control_port=self._control_port,
            control_socket=self._control_socket
        )
        if controller is not None:
            log.notice('New connection with Tor established.')

            ws_controller = websockets.ws_controller()
            ws_controller.listen_tor_log()
            init_bw_handler()

            try:
                # Listen for bandwidth events
                controller.add_event_listener(ws_controller.bw_event, EventType.BW)
                # Listen for changes in status of Tor control connection
                controller.add_status_listener(ws_controller.reset_listener)
                controller.add_status_listener(self._conn_listener)
                # Finally, send useful information to the client
                ws_controller.startup_info()
            except stem.ProtocolError as exc:
                log.warn('Unable to attach listeners: %s' % exc)
        else:
            log.notice('Unable to start establish a connection with Tor \
            control. Retrying in %s seconds.' % CONFIG['conn.loopInterval'])
