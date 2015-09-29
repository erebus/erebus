"""
"""
import json

import stem.util.log
import stem.util.enum

from cyclone.websocket import WebSocketHandler

from erebus.server.handlers import graph, info, log

WebSocketType = stem.util.enum.Enum(
    ('BANDWIDTH', 'bandwidth'), ('STATUS', 'status'), ('LOG', 'log'),
    ('INFO', 'info'),
)

WEBSOCKETS = None


def ws_controller():
    """
    Provides the websockets singleton.
    """

    return WEBSOCKETS


def init_websockets():
    """
    """

    global WEBSOCKETS
    WEBSOCKETS = WebSocketController()
    return WEBSOCKETS


class WebSocketController:
    """
    Tracks the global state of websockets
    """

    def __init__(self):
        """
        Initialize an empty list for each of the websocket types
        """

        self._websockets = dict([(ws_type, []) for ws_type in WebSocketType])

    def add_websocket(self, ws_type, ws):
        """
        Add an object to the list of active websockets of certain type.

        Arguments:
        ws_type - type of websocket to be fetched
        ws - websocket object to be added
        """

        if self._websockets[ws_type] is not None:
            if ws not in self._websockets[ws_type]:
                self._websockets[ws_type].append(ws)
        else:
            stem.util.log.notice('Undefined type (%s) when adding websocket' % ws_type)

    def remove_websocket(self, ws_type, ws):
        """
        Remove an object of the list of active websockets of certain type.

        Arguments:
        ws_type - type of websocket to be fetched
        ws - websocket object to be added
        """

        if self._websockets[ws_type] is not None:
            if ws in self._websockets[ws_type]:
                self._websockets[ws_type].remove(ws)
        else:
            stem.util.log.notice('Undefined type (%s) when removing websocket' % ws_type)

    def get_websockets(self, ws_type):
        """
        Provides a list of active websockets of a certain type.

        Arguments:
        ws_type - type of websocket to be fetched.
        """

        ws = self._websockets.get(ws_type, None)
        if ws is None:
            stem.util.log.notice('Undef type (%s) when retrieving websockets' % ws_type)
        return ws

    def send_data(self, ws_type, data):
        """
        Send JSON encoded data to a list of websockets of a certain type.

        Arguments:
        ws_type - type of websocket where the data will be sent
        data - dictionary
        """

        ws_listeners = self.get_websockets(ws_type)
        if ws_listeners is not None:
            for ws in ws_listeners:
                try:
                    ws.sendMessage(json.dumps(data))
                except FrameDecodeError as exc:
                    stem.util.log.error('Error while sending data to %s websocket: %s' % (ws.ws_type(), exc))

    def receive_message(self, message, ws):
        """
        Parse requests received from client.
        """
        message = json.loads(message)

        if ws.ws_type() == WebSocketType.BANDWIDTH:
            if message['request'] == 'BW-CACHE':
                bw = graph.bw_handler()
                if bw is not None:
                    self.send_data(ws.ws_type(), bw.get_cache())

        elif ws.ws_type() == WebSocketType.INFO:
            if message['request'] == 'INFO':
                self.send_data(ws.ws_type(), info.get_info())

        elif ws.ws_type() == WebSocketType.LOG:
            if message['request'] == 'LOG-CACHE':
                logger = log.log_handler()
                if logger is not None:
                    self.send_data(ws.ws_type(), logger.get_cache())
            if message['request'] == 'LOG-FILTER':
                logger = log.log_handler()
                if logger is not None:
                    log.update_filter()

    def bw_event(self, event):
        bw_stats = graph.bw_handler().get_info(event)
        self.send_data(WebSocketType.BANDWIDTH, bw_stats)

    def listen_erebus_log(self, logged_events):
        log.init_log_handler(logged_events, self._erebus_event)

    def listen_tor_log(self):
        logger = log.log_handler()
        logger.init_tor_log(self._tor_event)

    def _erebus_event(self, record):
        logger = log.log_handler()
        entry = logger._erebus_event(record)
        if entry is not None:
            self.send_data(WebSocketType.LOG, entry)

    def _tor_event(self, record):
        logger = log.log_handler()
        entry = logger._tor_event(record)
        if entry is not None:
            self.send_data(WebSocketType.LOG, entry)

    def reset_listener(self, controller, state, timestamp):
        current_status = info.get_status(state)
        self.send_data(WebSocketType.INFO, current_status)

    def startup_info(self):
        relay_info = info.get_info()
        self.send_data(WebSocketType.INFO, relay_info)


class BaseWSHandler(WebSocketHandler):
    """
    Base class to be implemented by each of the websockets erebus supports.
    E.g. Bandwidth, Log, Status, etc.
    """

    def getType(self):
        """
        Each subclass must define its type
        """

        raise NotImplementedError('Should be implemented by subclasses')

    def connectionMade(self, *args, **kwargs):
        """
        When a connection is made, keep track of it by adding it to
        websockets controller
        """

        ws = ws_controller()
        if ws is not None:
            ws.add_websocket(self.ws_type(), self)
            # log.info("New %s websocket opened" % self.ws_type())

    def connectionLost(self, reason):
        """
        When the connection its lost, remove it from websockets controller
        """

        ws = ws_controller()
        if ws is not None:
            ws.remove_websocket(self.ws_type(), self)
            # log.info("%s closed, reason: %s" % (self.ws_type(), reason))

    def messageReceived(self, message):
        """
        Requests from the client (protocol-like)
        """

        ws = ws_controller()
        if ws is not None:
            ws.receive_message(message, self)


class BandwidthWSHandler(BaseWSHandler):

    def ws_type(self):
        return WebSocketType.BANDWIDTH


class StatusWSHandler(BaseWSHandler):

    def ws_type(self):
        return WebSocketType.STATUS


class LogWSHandler(BaseWSHandler):

    def ws_type(self):
        return WebSocketType.LOG


class InfoWSHandler(BaseWSHandler):

    def ws_type(self):
        return WebSocketType.INFO
