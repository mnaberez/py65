import unittest
import sys
from py65 import util

class UtilTopLevelTests(unittest.TestCase):
  def test_itoa_decimal_output(self):
    self.assertEqual('10', util.itoa(10, base=10))
  
  def test_itoa_hex_output(self):
    self.assertEqual('a', util.itoa(10, base=16))
  
  def test_itoa_bin_output(self):
    self.assertEqual('1010', util.itoa(10, base=2))

class AddressParserTests(unittest.TestCase):
  def test_number_hex_literal(self):
    parser = util.AddressParser()
    self.assertEqual(49152, parser.number('$c000'))

  def test_number_dec_literal(self):
    parser = util.AddressParser()
    self.assertEqual(49152, parser.number('+49152'))

  def test_number_bin_literal(self):
    parser = util.AddressParser()
    self.assertEqual(129, parser.number('%10000001'))

  def test_number_default_radix(self):
    parser = util.AddressParser()
    parser.radix = 10
    self.assertEqual(10, parser.number('10'))
    parser.radix = 16
    self.assertEqual(16, parser.number('10'))
  
  def test_number_label(self):
    parser = util.AddressParser()
    parser.labels = {'foo': 0xC000}
    self.assertEquals(0xC000, parser.number('foo'))
  
  def test_number_bad_label(self):
    parser = util.AddressParser()
    try:
      parser.number('bad_label')
      self.fail()
    except KeyError, why:
      self.assertEqual('Label not found: bad_label', why[0])

  def test_number_label_hex_offset(self):
    parser = util.AddressParser()
    parser.labels = {'foo': 0xC000}
    self.assertEquals(0xC003, parser.number('foo+$3'))
    self.assertEquals(0xBFFD, parser.number('foo-$3'))
    self.assertEquals(0xC003, parser.number('foo + $3'))
    self.assertEquals(0xBFFD, parser.number('foo - $3'))

  def test_number_label_dec_offset(self):
    parser = util.AddressParser()
    parser.labels = {'foo': 0xC000}
    self.assertEquals(0xC003, parser.number('foo++3'))
    self.assertEquals(0xBFFD, parser.number('foo-+3'))
    self.assertEquals(0xC003, parser.number('foo + +3'))
    self.assertEquals(0xBFFD, parser.number('foo - +3'))

  def test_number_label_bin_offset(self):
    parser = util.AddressParser()
    parser.labels = {'foo': 0xC000}
    self.assertEquals(0xC003, parser.number('foo+%00000011'))
    self.assertEquals(0xBFFD, parser.number('foo-%00000011'))
    self.assertEquals(0xC003, parser.number('foo + %00000011'))
    self.assertEquals(0xBFFD, parser.number('foo - %00000011'))

  def test_number_label_offset_default_radix(self):
    parser = util.AddressParser()
    parser.labels = {'foo': 0xC000}
    parser.radix = 16
    self.assertEquals(0xC010, parser.number('foo+10'))
    self.assertEquals(0xBFF0, parser.number('foo-10'))
    self.assertEquals(0xC010, parser.number('foo + 10'))
    self.assertEquals(0xBFF0, parser.number('foo - 10'))    
    parser.radix = 10
    self.assertEquals(0xC00A, parser.number('foo+10'))
    self.assertEquals(0xBFF6, parser.number('foo-10'))
    self.assertEquals(0xC00A, parser.number('foo + 10'))
    self.assertEquals(0xBFF6, parser.number('foo - 10'))    
  
  def test_number_bad_label_with_offset(self):
    parser = util.AddressParser()
    try:
      parser.number('bad_label+3')
      self.fail()
    except KeyError, why:
      self.assertEqual('Label not found: bad_label', why[0])    
    

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
