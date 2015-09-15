"""
General purpose utilities.
"""

import os
import sys

import stem.connection
import stem.util.conf
import stem.util.enum
import stem.util.log

TOR_CONTROLLER = None
LOG_HANDLER = None
BASE_DIR = os.path.sep.join(__file__.split(os.path.sep)[:-2])
TESTING = False
DUAL_MODE = False

try:
    uses_settings = stem.util.conf.uses_settings(
        'erebus', os.path.join(BASE_DIR, 'config'), lazy_load=False)
except IOError as exc:
    print("Unable to load rwsd's internal configurations: %s" % exc)
    sys.exit(1)


def tor_controller():
    """
    Singleton for getting our tor controller connection.

    :returns: :class:`~stem.control.Controller`
    """

    return TOR_CONTROLLER


def init_tor_controller(*args, **kwargs):
    """
    Sets the Controller used by rwsd. This is a passthrough for Stem's
    :func:`~stem.connection.connect` function.

    :returns: :class:`~stem.control.Controller`
    """

    global TOR_CONTROLLER
    TOR_CONTROLLER = stem.connection.connect(*args, **kwargs)
    return TOR_CONTROLLER


@uses_settings
def msg(message, config, **attr):
    """
    Provides the given message.

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
    Whether to run erebus in separated scripts (server and clients in
    different ports) or in dual mode (both on same port)
    """

    return DUAL_MODE


def set_dual_mode():
    """
    Set dual mode to True.
    """

    global DUAL_MODE
    DUAL_MODE = True
