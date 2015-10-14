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
Runs pep8 and pyflakes tests.
"""

import os

import stem.util.conf
import stem.util.test_tools

import erebus.util

EREBUS_BASE = os.path.dirname(__file__)

SRC_PATHS = [os.path.join(EREBUS_BASE, path) for path in (
    'erebus',
    'run_tests.py',
    'run_erebus.py',
)]


@erebus.util.uses_settings
def main():
    orphaned_pyc = stem.util.test_tools.clean_orphaned_pyc(EREBUS_BASE)

    for path in orphaned_pyc:
        print('Deleted orphaned pyc file: %s' % path)

    static_check_issues = {}

    if stem.util.test_tools.is_pyflakes_available():
        pyflakes_issues = stem.util.test_tools.pyflakes_issues(SRC_PATHS)

        for path, issues in pyflakes_issues.items():
            for issue in issues:
                static_check_issues.setdefault(path, []).append(issue)

    if stem.util.test_tools.is_pep8_available():
        pep8_issues = stem.util.test_tools.stylistic_issues(
            SRC_PATHS,
            check_two_space_indents=True,
            check_newlines=True,
            check_trailing_whitespace=True,
            check_exception_keyword=True,
            prefer_single_quotes=True,
        )

        for path, issues in pep8_issues.items():
            for issue in issues:
                static_check_issues.setdefault(path, []).append(issue)

    if static_check_issues:
        print('STATIC CHECKS')

        for file_path in static_check_issues:
            print('* %s' % file_path)

            for issue in static_check_issues[file_path]:
                print('  line %-4s - %-40s %s' % (
                    issue.line_number, issue.message, issue.line))

            print


if __name__ == '__main__':
    main()
