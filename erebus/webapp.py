"""
"""
import cyclone.web

from stem.util import log

from erebus.client import CLIENT_SETTINGS, CLIENT_HANDLERS
from erebus.server import SERVER_SETTINGS, SERVER_HANDLERS
from erebus.util import dual_mode


class Application(cyclone.web.Application):

    def __init__(self, is_client=False):
        if is_client:
            settings = CLIENT_SETTINGS
            handlers = CLIENT_HANDLERS
        else:
            # Run server handlers together with client handler.
            # This is useful if we are running on localhost and don't want
            # to run two scripts in different ports
            if dual_mode():
                try:
                    # Join handlers and settings from both server and client
                    for item in CLIENT_HANDLERS:
                        SERVER_HANDLERS.append(item)
                    SERVER_SETTINGS.update(CLIENT_SETTINGS)
                except ImportError as exc:
                    log.warn('Unable to start in dual mode. %s' % exc)

            settings = SERVER_SETTINGS
            handlers = SERVER_HANDLERS

        cyclone.web.Application.__init__(self, handlers, **settings)
