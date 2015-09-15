#!/usr/bin/env python
import sys

from twisted.python import log

import erebus

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    erebus.main()
