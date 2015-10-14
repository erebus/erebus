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
Cyclone web application that runs with client or server settings.
(or both if dual mode is enabled).
"""

import cyclone.web

from erebus.client import CLIENT_SETTINGS, CLIENT_HANDLERS
from erebus.server import SERVER_SETTINGS, SERVER_HANDLERS
from erebus.util import dual_mode


class Application(cyclone.web.Application):

    def __init__(self, is_client=False):
        """
        Load client or server settings and handlers (or both).
        """
        if is_client:
            settings = CLIENT_SETTINGS
            handlers = CLIENT_HANDLERS
        else:
            # If dual mode is set, join handlers and settings of both
            # client and server
            if dual_mode():
                for item in CLIENT_HANDLERS:
                    SERVER_HANDLERS.append(item)
                SERVER_SETTINGS.update(CLIENT_SETTINGS)

            settings = SERVER_SETTINGS
            handlers = SERVER_HANDLERS

        cyclone.web.Application.__init__(self, handlers, **settings)
