import sys
import unittest
from py65.utils.conversions import itoa, convert_to_bin, convert_to_bcd


class ConversionsTopLevelTests(unittest.TestCase):
    def test_itoa_decimal_output(self):
        self.assertEqual('10', itoa(10, base=10))
        self.assertEqual('-10', itoa(-10, base=10))

    def test_itoa_hex_output(self):
        self.assertEqual('a', itoa(10, base=16))
        self.assertEqual('-a', itoa(-10, base=16))

    def test_itoa_bin_output(self):
        self.assertEqual('1010', itoa(10, base=2))
        self.assertEqual('-1010', itoa(-10, base=2))

    def test_convert_to_bin(self):
        self.assertEqual(0, convert_to_bin(0))
        self.assertEqual(99, convert_to_bin(0x99))

    def test_convert_to_bcd(self):
        self.assertEqual(0, convert_to_bcd(0))
        self.assertEqual(0x99, convert_to_bcd(99))

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
