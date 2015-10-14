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
Websocket-related functions, including the main websockets controller,
base websocket class and custom websocket classes (such as bandwidth, log).
"""

import json

import cyclone.websocket
import stem.util.log
import stem.util.enum

from erebus.server.handlers import graph, info, log
from erebus.util import msg

WebSocketType = stem.util.enum.Enum(
    ('BANDWIDTH', 'bandwidth'), ('STATUS', 'status'), ('LOG', 'log'),
    ('INFO', 'info'),
)

WEBSOCKETS = None


def ws_controller():
    """
    Provides the WEBSOCKETS singleton.

    :returns: :class:`~erebus.server.websockets.WebSocketController`
    """

    return WEBSOCKETS


def init_websockets():
    """
    Initializes the websockets controller instance and returns the instance.

    :returns: :class:`~erebus.server.websockets.WebSocketController`
    """

    global WEBSOCKETS
    WEBSOCKETS = WebSocketController()
    return WEBSOCKETS


class WebSocketController:
    """
    Tracks the global state of websockets.
    """

    def __init__(self):
        """
        Initialize an empty list for each of the websocket types.
        """

        self._websockets = dict([(ws_type, []) for ws_type in WebSocketType])

    def add_websocket(self, ws_type, ws):
        """
        Adds a websocket object to the list of active websockets of a
        certain type.

        :param str ws_type: string indicating type of websocket.
        :param Class ws: :class:`~cyclone.websocket.WebSocketHandler` to
          be added to the list of active websockets.
        """

        if self._websockets[ws_type] is not None:
            if ws not in self._websockets[ws_type]:
                self._websockets[ws_type].append(ws)
        else:
            stem.util.log.notice(msg('ws.add_error', type=ws_type))

    def remove_websocket(self, ws_type, ws):
        """
        Removes a websocket object of the list of active websockets of a
        certain type.

        :param str ws_type: string indicating type of websocket.
        :param Class ws: :class:`~cyclone.websocket.WebSocketHandler` to
          be removed from the list of active websockets.
        """

        if self._websockets[ws_type] is not None:
            if ws in self._websockets[ws_type]:
                self._websockets[ws_type].remove(ws)
        else:
            stem.util.log.notice(msg('ws.remove_error', type=ws_type))

    def get_websockets(self, ws_type):
        """
        Provides a list of active websockets of a certain type.

        :param str ws_type: string indicating type of websocket.
        """

        ws = self._websockets.get(ws_type, None)
        if ws is None:
            stem.util.log.notice(msg('ws.get_error', type=ws_type))
        return ws

    def send_data(self, ws_type, data):
        """
        Send JSON encoded data to a list of websockets of a certain type.

        :param str ws_type: string indicating type of websocket.
        :param dict data: data to be encoded in JSON.
        """

        ws_listeners = self.get_websockets(ws_type)
        if ws_listeners is not None:
            for ws in ws_listeners:
                try:
                    ws.sendMessage(json.dumps(data))
                except cyclone.websocket.FrameDecodeError as exc:
                    stem.util.log.error(
                        msg('ws.send_error', type=ws_type, error=exc))

    def receive_message(self, message, ws):
        """
        Parse requests received from the client. This requests could be
        addressed to any of the websocket types, and they consist of
        plain-text messages.

        :param str message: string containing a plain-text message to be
          parsed.
        :param Class ws: :class:`~cyclone.websocket.WebSocketHandler` to
          which the message was sent.
        """

        message = json.loads(message)

        # TODO: check for proper format of message
        # Currently we are assuming the message its valid

        if ws.ws_type() == WebSocketType.BANDWIDTH:
            # Bandwidth cache was requested
            if message['request'] == 'BW-CACHE':
                bw = graph.bw_handler()
                if bw is not None:
                    self.send_data(ws.ws_type(), bw.get_cache())

        elif ws.ws_type() == WebSocketType.INFO:
            # Relay info was requested. This is info must be delivered upon
            # a request is received by the client, since it's not like BW
            # or LOG events which are sent by tor events.
            if message['request'] == 'INFO':
                self.send_data(ws.ws_type(), info.get_info())

        elif ws.ws_type() == WebSocketType.LOG:
            # Log cache was requested
            if message['request'] == 'LOG-CACHE':
                logger = log.log_handler()
                if logger is not None:
                    self.send_data(ws.ws_type(), logger.get_cache())
            # A log filter was sent
            if message['request'] == 'LOG-FILTER':
                logger = log.log_handler()
                if logger is not None:
                    log.update_filter()

    def bw_event(self, event):
        """
        Handler for BW event, to be attached as a listener to tor controller.
        Whenever an event is received, get BW info and send it through
        BW websocket.

        :param Class event: :class:`~stem.response.events.Event` delivered
          by stem.
        """
        bw_stats = graph.bw_handler().get_info(event)
        self.send_data(WebSocketType.BANDWIDTH, bw_stats)

    def listen_erebus_log(self, logged_events):
        """
        Handler to initialize erebus log listening. This function will be
        called when erebus is started and will receive a list of events
        to listen for.

        :param set logged_events: **set** of event types to listen.
        """
        log.init_log_handler(logged_events, self._erebus_event)

    def listen_tor_log(self):
        """
        Handler to initialize tor log listening. This function will be
        called when a tor control connection is made. The set of events
        to listen for are already supposed to be configured by previously
        calling listen_erebus_log.
        """
        logger = log.log_handler()
        logger.init_tor_log(self._tor_event)

    def _erebus_event(self, record):
        """
        Handler for listening to single erebus events.

        :param record: log entry formatted by `~stem.util.log`
        """
        logger = log.log_handler()
        entry = logger._erebus_event(record)
        if entry is not None:
            self.send_data(WebSocketType.LOG, entry)

    def _tor_event(self, record):
        """
        Handler for listening to single tor events.

        :param Class record: a valid :class:`~stem.response.` subclass.
        """
        logger = log.log_handler()
        entry = logger._tor_event(record)
        if entry is not None:
            self.send_data(WebSocketType.LOG, entry)

    def reset_listener(self, controller, state, timestamp):
        """
        Handler to be called whenever the connection to tor is lost, so
        to notice the client that tor is down. This function is attached
        as a status listener, so it will be called by stem.

        :param Class controller: :class:`~stem.control.BaseController`.
        :param Class state: :class:`~stem.control.State` enumeration for
          states that a controller can have.
        :param float timestamp: Unix timestamp.
        """
        current_status = info.get_status(state)
        self.send_data(WebSocketType.INFO, current_status)

    def startup_info(self):
        """
        Handler to be called when a tor control connection is made and
        it's necessary to send relay info to the client.
        """
        relay_info = info.get_info()
        self.send_data(WebSocketType.INFO, relay_info)


class BaseWSHandler(cyclone.websocket.WebSocketHandler):
    """
    Base class to be implemented by custom websockets.
    """

    def getType(self):
        """
        Each subclass must define its type.

        :raises: **NotImplementedError** if the subclass doesn't implement
          this.
        """

        raise NotImplementedError('Should be implemented by subclasses')

    def connectionMade(self, *args, **kwargs):
        """
        When a connection is made, keep track of it by adding it to
        websocket controller.
        """

        ws = ws_controller()
        if ws is not None:
            ws.add_websocket(self.ws_type(), self)
            stem.util.log.debug(msg('ws.opened', type=self.ws_type()))

    def connectionLost(self, reason):
        """
        Remove websocket from websocket controller when the connection is lost.

        :param str reason: reason why the connection was lost.
        """

        ws = ws_controller()
        if ws is not None:
            ws.remove_websocket(self.ws_type(), self)
            stem.util.log.debug(
                msg('ws.opened', type=self.ws_type(), reason=reason))

    def messageReceived(self, message):
        """
        Gets called when a message is received from the client.

        :param str message: plain text message that was received.
        """

        ws = ws_controller()
        if ws is not None:
            # Pass message to websocket controller
            ws.receive_message(message, self)


class BandwidthWSHandler(BaseWSHandler):
    """
    Bandwidth websocket subclass.
    """

    def ws_type(self):
        return WebSocketType.BANDWIDTH


class StatusWSHandler(BaseWSHandler):
    """
    Status websocket subclass (status refers to state of tor control
    connection).
    """

    def ws_type(self):
        return WebSocketType.STATUS


class LogWSHandler(BaseWSHandler):
    """
    Log websocket subclass.
    """

    def ws_type(self):
        return WebSocketType.LOG


class InfoWSHandler(BaseWSHandler):
    """
    (Relay) info websocket subclass.
    """

    def ws_type(self):
        return WebSocketType.INFO
