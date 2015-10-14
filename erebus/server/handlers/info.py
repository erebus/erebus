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
Relay info functions, including fingerprint, nickname, tor version, etc.
"""

from stem.control import State

from erebus.util import tor_controller


def get_info():
    """
    Get relay info. This function can be called by the client at any time,
    so it might be the case this info is requested even when tor is down.

    :returns: dictionary with relay information.
    """

    controller = tor_controller()
    if controller is not None:
        output = {
            'fingerprint': controller.get_info('fingerprint', 'Unknown'),
            'nickname': controller.get_conf('Nickname', ''),
            'version': str(controller.get_version('Unknown')).split()[0],
            'status': 'online'
        }
    else:
        output = {'status': 'offline'}

    return output


def get_status(state):
    """
    Just return the current state of tor control connection.

    :returns: dictionary with tor control connection state.
    """

    return {'status': 'offline' if state == State.CLOSED else 'online'}
