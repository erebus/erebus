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
General purpose utilities.
"""

import os
import sys

import stem.connection
import stem.util.conf
import stem.util.enum
import stem.util.log


BASE_DIR = os.path.sep.join(__file__.split(os.path.sep)[:-2])

DUAL_MODE, TESTING = False, False

TOR_CONTROLLER, LOG_HANDLER = None, None

try:
    uses_settings = stem.util.conf.uses_settings(
        'erebus', os.path.join(BASE_DIR, 'config'), lazy_load=False)
except IOError as exc:
    print("Unable to load rwsd's internal configurations: %s" % exc)
    sys.exit(1)


def tor_controller():
    """
    Provides the TOR_CONTROLLER singleton.

    :returns: :class:`~stem.control.Controller`
    """

    return TOR_CONTROLLER


def init_tor_controller(*args, **kwargs):
    """
    Initializes the tor controller instance. This is a passthrough for
    Stem's :func:`~stem.connection.connect` function.

    :returns: :class:`~stem.control.Controller`
    """

    global TOR_CONTROLLER
    TOR_CONTROLLER = stem.connection.connect(*args, **kwargs)
    return TOR_CONTROLLER


@uses_settings
def msg(message, config, **attr):
    """
    Provides the given message read from strings config file.

    :param str message: message handle to log
    :param dict attr: attributes to format the message with

    :returns: **str** that was requested
    """

    try:
        return config.get('msg.%s' % message).format(**attr)
    except:
        msg = 'BUG: We attempted to use an undefined string \
            resource (%s)' % message

        if TESTING:
            raise ValueError(msg)

        stem.util.log.notice(msg)
        return ''


def dual_mode():
    """
    Whether to run erebus with server or client functionalities, or both.

    :returns: **bool** answer
    """

    return DUAL_MODE


def set_dual_mode():
    """
    Sets DUAL_MODE to True.
    """

    global DUAL_MODE
    DUAL_MODE = True
