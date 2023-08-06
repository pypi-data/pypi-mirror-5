# -*- coding: utf-8 -*-
import logging
if __name__ == '__main__':
    logging.basicConfig()
_log = logging.getLogger(__name__)

import sys
import pyxb
import unittest

class TestTrac0132 (unittest.TestCase):
    message = u'bad character \u2620'
    def testDecode (self):
        e = pyxb.PyXBException(self.message)
        if sys.version_info[:2] > (2, 4):
            self.assertEqual(self.message, e.args[0])

if __name__ == '__main__':
    unittest.main()
