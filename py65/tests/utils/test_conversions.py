import sys
import unittest
from py65.utils.conversions import itoa


class ConversionsTopLevelTests(unittest.TestCase):
    def test_itoa_decimal_output(self):
        self.assertEqual('10', itoa(10, base=10))

    def test_itoa_hex_output(self):
        self.assertEqual('a', itoa(10, base=16))

    def test_itoa_bin_output(self):
        self.assertEqual('1010', itoa(10, base=2))


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
