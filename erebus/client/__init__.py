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
Define handlers and settings for the client app.
"""

import os.path

import stem.util.enum

from erebus.client import handlers

BASE_DIR = os.path.sep.join(__file__.split(os.path.sep)[:-2])

ClientHandlers = stem.util.enum.Enum(('DASHBOARD', r"/"))

# List of client routes and their handlers. In this case, just a handler
# to render the dashboard, which is an AngularJS app.
CLIENT_HANDLERS = [
    (ClientHandlers.DASHBOARD, handlers.DashboardHandler),
]

# The client needs to use templates (HTML) and static files (JS and CSS)
CLIENT_SETTINGS = {
    'template_path': os.path.join(BASE_DIR, 'client/templates'),
    'static_path': os.path.join(BASE_DIR, 'client/static'),
    'autoescape': None
}
