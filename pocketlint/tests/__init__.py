# Copyright (C) 2011-2013 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import sys
import unittest

from pocketlint.formatcheck import Reporter


class CheckerTestCase(unittest.TestCase):
    """A testcase with a TestReporter for checkers."""

    python_version = sys.version_info

    def setUp(self):
        self.reporter = Reporter(Reporter.COLLECTOR)
        self.reporter.call_count = 0

    def write_to_file(self, wfile, string):
        if sys.version_info >= (3,):
            string = bytes(string, 'utf-8')
        wfile.write(string)
        wfile.flush()
