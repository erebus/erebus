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
Define handlers and settings for the server app.
"""

import stem.util.enum

from erebus.server import websockets

ServerHandlers = stem.util.enum.Enum(
    ('BANDWIDTH', r"/bandwidth"),
    ('LOG', r"/log"),
    ('INFO', r"/info"),
)

# List of server routes and their handlers (websockets)
SERVER_HANDLERS = [
    (ServerHandlers.BANDWIDTH, websockets.BandwidthWSHandler),
    (ServerHandlers.LOG, websockets.LogWSHandler),
    (ServerHandlers.INFO, websockets.InfoWSHandler),
]

# No special settings for the server (for now).
SERVER_SETTINGS = {}
