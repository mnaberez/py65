import unittest
import sys
import re
from monitor import Monitor

class MonitorTests(unittest.TestCase):
  def test__parsenum_hex_literal(self):
    mon = Monitor()
    self.assertEqual(49152, mon._parsenum('$c000'))

  def test__parsenum_dec_literal(self):
    mon = Monitor()
    self.assertEqual(49152, mon._parsenum('+49152'))

  def test__parsenum_bin_literal(self):
    mon = Monitor()
    self.assertEqual(129, mon._parsenum('%10000001'))

  def test__parsenum_default_radix(self):
    mon = Monitor()
    mon._radix = 10
    self.assertEqual(10, mon._parsenum('10'))
    mon._radix = 16
    self.assertEqual(16, mon._parsenum('10'))
  
  def test__parsenum_label(self):
    mon = Monitor()
    mon._labels = {'foo': 0xC000}
    self.assertEquals(0xC000, mon._parsenum('foo'))
  
  def test__parsenum_bad_label(self):
    mon = Monitor()
    try:
      mon._parsenum('bad_label')
      self.fail()
    except KeyError, why:
      self.assertEqual('Label not found: bad_label', why[0])

  def test__parsenum_label_hex_offset(self):
    mon = Monitor()
    mon._labels = {'foo': 0xC000}
    self.assertEquals(0xC003, mon._parsenum('foo+$3'))
    self.assertEquals(0xBFFD, mon._parsenum('foo-$3'))
    self.assertEquals(0xC003, mon._parsenum('foo + $3'))
    self.assertEquals(0xBFFD, mon._parsenum('foo - $3'))

  def test__parsenum_label_dec_offset(self):
    mon = Monitor()
    mon._labels = {'foo': 0xC000}
    self.assertEquals(0xC003, mon._parsenum('foo++3'))
    self.assertEquals(0xBFFD, mon._parsenum('foo-+3'))
    self.assertEquals(0xC003, mon._parsenum('foo + +3'))
    self.assertEquals(0xBFFD, mon._parsenum('foo - +3'))

  def test__parsenum_label_bin_offset(self):
    mon = Monitor()
    mon._labels = {'foo': 0xC000}
    self.assertEquals(0xC003, mon._parsenum('foo+%00000011'))
    self.assertEquals(0xBFFD, mon._parsenum('foo-%00000011'))
    self.assertEquals(0xC003, mon._parsenum('foo + %00000011'))
    self.assertEquals(0xBFFD, mon._parsenum('foo - %00000011'))

  def test__parsenum_label_offset_default_radix(self):
    mon = Monitor()
    mon._labels = {'foo': 0xC000}
    mon._radix = 16
    self.assertEquals(0xC010, mon._parsenum('foo+10'))
    self.assertEquals(0xBFF0, mon._parsenum('foo-10'))
    self.assertEquals(0xC010, mon._parsenum('foo + 10'))
    self.assertEquals(0xBFF0, mon._parsenum('foo - 10'))    
    mon._radix = 10
    self.assertEquals(0xC00A, mon._parsenum('foo+10'))
    self.assertEquals(0xBFF6, mon._parsenum('foo-10'))
    self.assertEquals(0xC00A, mon._parsenum('foo + 10'))
    self.assertEquals(0xBFF6, mon._parsenum('foo - 10'))    
  
  def test__parsenum_bad_label_with_offset(self):
    mon = Monitor()
    try:
      mon._parsenum('bad_label+3')
      self.fail()
    except KeyError, why:
      self.assertEqual('Label not found: bad_label', why[0])    
  
def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
