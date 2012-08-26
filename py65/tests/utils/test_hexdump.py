import unittest
import sys
from py65.utils.hexdump import load, Loader

class TopLevelHexdumpTests(unittest.TestCase):
    def test_load(self):
        text = 'c000: aa bb'
        start, data = load(text)
        self.assertEqual(0xC000, start)
        self.assertEqual([0xAA, 0xBB], data)

class HexdumpLoaderTests(unittest.TestCase):
    def test_empty_string_does_nothing(self):
        text = ''
        loader = Loader(text)
        self.assertEqual(None, loader.start_address)
        self.assertEqual([], loader.data)

    def test_all_whitespace_does_nothing(self):
        text = "  \r\n  \t  \n"
        loader = Loader(text)
        self.assertEqual(None, loader.start_address)
        self.assertEqual([], loader.data)       
   
    def test_raises_when_start_address_not_found(self):
        text = 'aa bb cc'
        try:
            Loader(text)
            self.fail()
        except ValueError, why:
            msg = 'Start address was not found in data'
            self.assert_(why[0].startswith('Start address'))

    def test_raises_when_start_address_is_invalid(self):
        text = 'oops: aa bb cc'
        try:
            Loader(text)
            self.fail()
        except ValueError, why:                   
            msg = 'Could not parse address: oops'
            self.assertEqual(msg, why[0])

    def test_raises_when_start_address_is_too_short(self):
        text = '01: aa bb cc'
        try:
            Loader(text)
            self.fail()
        except ValueError, why:                   
            msg = 'Expected address to be 2 bytes, got 1'
            self.assertEqual(msg, why[0])

    def test_raises_when_start_address_is_too_long(self):
        text = '010304: aa bb cc'
        try:
            Loader(text)
            self.fail()
        except ValueError, why:                   
            msg = 'Expected address to be 2 bytes, got 3'
            self.assertEqual(msg, why[0])

    def test_raises_when_next_address_is_unexpected(self):
        text = "c000: aa\nc002: cc"
        try:
            Loader(text)
            self.fail()
        except ValueError, why:
            msg = 'Non-contigous block detected.  Expected next ' \
                  'address to be $c001, label was $c002'
            self.assertEqual(msg, why[0])
    
    def test_raises_when_data_is_invalid(self):
        text = 'c000: foo'
        try:
            Loader(text)
            self.fail()
        except ValueError, why:
            msg = 'Could not parse data: foo'
            self.assertEqual(msg, why[0]) 

    def test_loads_data_without_dollar_signs(self):
        text = 'c000: aa bb'
        load = Loader(text)
        self.assertEqual(0xC000, load.start_address)
        self.assertEqual([0xAA, 0xBB], load.data)

    def test_loads_data_with_some_dollar_signs(self):
        text = '$c000: aa $bb'
        load = Loader(text)
        self.assertEqual(0xC000, load.start_address)
        self.assertEqual([0xAA, 0xBB], load.data)

    def test_loads_multiline_data_with_unix_endings(self):
        text = '$c000: aa bb\n$c002: cc'
        load = Loader(text)
        self.assertEqual(0xC000, load.start_address)
        self.assertEqual([0xAA, 0xBB, 0xCC], load.data)

    def test_loads_multiline_data_with_dos_endings(self):
        text = '$c000: aa bb\r\n$c002: cc'
        load = Loader(text)
        self.assertEqual(0xC000, load.start_address)
        self.assertEqual([0xAA, 0xBB, 0xCC], load.data)
    
    def test_ignores_semicolon_comments(self):
        text = 'c000: aa bb ;comment'
        load = Loader(text)
        self.assertEqual(0xC000, load.start_address)
        self.assertEqual([0xAA, 0xBB], load.data)
    
    def test_ignores_double_dash_comments(self):
        text = 'c000: aa bb -- comment'
        load = Loader(text)
        self.assertEqual(0xC000, load.start_address)
        self.assertEqual([0xAA, 0xBB], load.data)
    
    def test_ignores_pound_comments(self):
        text = 'c000: aa bb # comment'
        load = Loader(text)
        self.assertEqual(0xC000, load.start_address)
        self.assertEqual([0xAA, 0xBB], load.data)
    
    def test_ignores_pound_comments(self):
        text = 'c000: aa bb # comment'
        load = Loader(text)
        self.assertEqual(0xC000, load.start_address)
        self.assertEqual([0xAA, 0xBB], load.data)
        
        

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
