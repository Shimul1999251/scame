# Copyright (C) 2011-2012 - Curtis Hovey <sinzui.is at verizon.net>
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

    def setUp(self):
        self.reporter = Reporter(Reporter.COLLECTOR)
        self.reporter.call_count = 0

    def write_to_file(self, wfile, string):
        if int(sys.version[0]) > 2:
            string = bytes(string, 'utf8')
        wfile.write(string)
        wfile.flush()
