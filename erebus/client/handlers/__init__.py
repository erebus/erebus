"""
Dashboard handler.
Just render index.html because all logic is done with AngularJS.
"""
import cyclone.web

from erebus.server import ServerHandlers
from erebus.util import uses_settings


class DashboardHandler(cyclone.web.RequestHandler):
    """
    """

    @uses_settings
    def get(self, config):
        """
        """

        conf = {
            'server.address': config.get('server.address'),
            'server.port': config.get('server.port'),
            'websockets': {},
        }
        # Add server handlers as websockets addresses
        # Thus, the Angular app will know where to fetch info
        # E.g.
        # server_config.ws[bandwidth] = /bw
        for k in ServerHandlers.keys():
            conf['websockets'][k.lower()] = ServerHandlers.__getitem__(k)

        self.render('index.html', config=conf)
