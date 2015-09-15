"""
erebus - Tor Relay Web Dashboard.
"""
import sys

__version__ = '0.1.0-dev'
__release_date__ = 'August 28, 2015'
__author__ = 'clv'
__contact__ = 'clv@riseup.net'
__url__ = 'http://github.com/leivaburto/erebus'
__license__ = 'TBA'

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
