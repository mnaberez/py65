import unittest
import sys
from py65.utils.addressing import AddressParser

class AddressParserTests(unittest.TestCase):
    def test_maxwidth_can_be_set_in_constructor(self):
        parser = AddressParser(maxwidth=24)
        self.assertEqual(24, parser.maxwidth)
        self.assertEqual(0xFFFFFF, parser._maxaddr)

    def test_maxwidth_defaults_to_16_bits(self):
        parser = AddressParser()
        self.assertEqual(16, parser.maxwidth)
        self.assertEqual(0xFFFF, parser._maxaddr)

    def test_maxwidth_setter(self):
        parser = AddressParser()
        parser.maxwidth = 24
        self.assertEqual(24, parser.maxwidth)
        self.assertEqual(0xFFFFFF, parser._maxaddr)

    def test_number_hex_literal(self):
        parser = AddressParser()
        self.assertEqual(49152, parser.number('$c000'))

    def test_number_dec_literal(self):
        parser = AddressParser()
        self.assertEqual(49152, parser.number('+49152'))

    def test_number_bin_literal(self):
        parser = AddressParser()
        self.assertEqual(129, parser.number('%10000001'))

    def test_number_default_radix(self):
        parser = AddressParser()
        parser.radix = 10
        self.assertEqual(10, parser.number('10'))
        parser.radix = 16
        self.assertEqual(16, parser.number('10'))

    def test_number_label(self):
        parser = AddressParser()
        parser.labels = {'foo': 0xC000}
        self.assertEqual(0xC000, parser.number('foo'))

    def test_number_bad_label(self):
        parser = AddressParser()
        try:
            parser.number('bad_label')
            self.fail()
        except KeyError, why:
            self.assertEqual('Label not found: bad_label', why[0])

    def test_number_label_hex_offset(self):
        parser = AddressParser()
        parser.labels = {'foo': 0xC000}
        self.assertEqual(0xC003, parser.number('foo+$3'))
        self.assertEqual(0xBFFD, parser.number('foo-$3'))
        self.assertEqual(0xC003, parser.number('foo + $3'))
        self.assertEqual(0xBFFD, parser.number('foo - $3'))

    def test_number_label_dec_offset(self):
        parser = AddressParser()
        parser.labels = {'foo': 0xC000}
        self.assertEqual(0xC003, parser.number('foo++3'))
        self.assertEqual(0xBFFD, parser.number('foo-+3'))
        self.assertEqual(0xC003, parser.number('foo + +3'))
        self.assertEqual(0xBFFD, parser.number('foo - +3'))

    def test_number_label_bin_offset(self):
        parser = AddressParser()
        parser.labels = {'foo': 0xC000}
        self.assertEqual(0xC003, parser.number('foo+%00000011'))
        self.assertEqual(0xBFFD, parser.number('foo-%00000011'))
        self.assertEqual(0xC003, parser.number('foo + %00000011'))
        self.assertEqual(0xBFFD, parser.number('foo - %00000011'))

    def test_number_label_offset_default_radix(self):
        parser = AddressParser()
        parser.labels = {'foo': 0xC000}
        parser.radix = 16
        self.assertEqual(0xC010, parser.number('foo+10'))
        self.assertEqual(0xBFF0, parser.number('foo-10'))
        self.assertEqual(0xC010, parser.number('foo + 10'))
        self.assertEqual(0xBFF0, parser.number('foo - 10'))
        parser.radix = 10
        self.assertEqual(0xC00A, parser.number('foo+10'))
        self.assertEqual(0xBFF6, parser.number('foo-10'))
        self.assertEqual(0xC00A, parser.number('foo + 10'))
        self.assertEqual(0xBFF6, parser.number('foo - 10'))

    def test_number_bad_label_with_offset(self):
        parser = AddressParser()
        try:
            parser.number('bad_label+3')
            self.fail()
        except KeyError, why:
            self.assertEqual('Label not found: bad_label', why[0])

    def test_number_truncates_address_at_maxwidth_16(self):
        parser = AddressParser()
        parser.labels = {'foo': 0xFFFF}
        self.assertEqual(0xFFFF, parser.number('foo+5'))

    def test_number_truncates_address_at_maxwidth_24(self):
        parser = AddressParser()
        parser.maxwidth = 24
        parser.labels = {'foo': 0xFFFFFF}
        self.assertEqual(0xFFFFFF, parser.number('foo+5'))

    def test_label_for_returns_label(self):
        parser = AddressParser(labels={'chrout':0xFFD2})
        self.assertEqual('chrout', parser.label_for(0xFFD2))

    def test_label_for_returns_none_by_default(self):
        parser = AddressParser(labels={})
        self.assertEqual(None, parser.label_for(0xFFD2))

    def test_label_for_returns_alternate_default(self):
        parser = AddressParser(labels={})
        self.assertEqual('foo', parser.label_for(0xFFD2, 'foo'))


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
