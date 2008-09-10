import unittest
import sys
import re
from py65.monitor import Monitor

class MonitorTests(unittest.TestCase):
    pass
  
def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
