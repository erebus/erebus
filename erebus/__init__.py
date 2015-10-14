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

import sys

__version__ = '0.1.0-dev'
__release_date__ = 'August 28, 2015'
__author__ = 'Cristobal Leiva'
__contact__ = 'clv@riseup.net'
__url__ = 'https://github.com/erebus/erebus'
__license__ = 'BSD'

__all__ = [
    'starter',
    'webapp',
]


def main():
    # try:
    import erebus.starter
    erebus.starter.main()
    # except ImportError as exc:
    # TODO: check dependencies for client and server
    # print('Unable to start erebus: %s' % exc)

    sys.exit(1)
