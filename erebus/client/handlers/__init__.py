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
Dashboard handler. Just render index.html because all the client logic
is done with AngularJS.
"""

import cyclone.web

from erebus.server import ServerHandlers
from erebus.util import uses_settings


class DashboardHandler(cyclone.web.RequestHandler):

    @uses_settings
    def get(self, config):
        """
        This method will be called when a HTTP GET request is made
        to the DashboardHandler.
        """

        # Config params to be passed to the AngularJS app.
        conf = {
            'server.address': config.get('server.address'),
            'server.port': config.get('server.port'),
            'websockets.protocol': config.get('websockets.protocol'),
            'websockets': {},
            'events.filter': config.get('startup.events'),
        }
        # List of websocket and their routes.
        # conf['websockets'] : {
        #   'bandwidth' : '/bw',
        #   'log': '/log',
        # }
        for k in ServerHandlers.keys():
            conf['websockets'][k.lower()] = ServerHandlers.__getitem__(k)

        self.render('index.html', config=conf)
