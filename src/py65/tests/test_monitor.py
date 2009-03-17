import unittest
import sys
import re
from py65.monitor import Monitor
from StringIO import StringIO

class MonitorTests(unittest.TestCase):

    # quit

    def test_do_EOF(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)    
        exitnow = mon.do_EOF('')
        self.assertEqual(True, exitnow)

    def test_help_EOF(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_EOF()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("To quit,"))

    def test_do_quit(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)    
        exitnow = mon.do_quit('')
        self.assertEqual(True, exitnow)

    def test_help_quit(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_EOF()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("To quit,"))
   
    # version
    
    def test_do_version(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_version('')
        out = stdout.getvalue()       
        self.assertTrue(out.startswith("\nPy65"))

    def test_help_version(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_version()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("version\t"))

    # reset
    
    def test_do_reset(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        old_mpu = mon._mpu
        mon.do_reset('')
        self.assertNotEqual(old_mpu, mon._mpu)

    def test_help_reset(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_reset()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("reset\t"))        

   # tilde
   
    def test_do_tilde(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_tilde('$10')
        out = stdout.getvalue()  
        expected = "+16\n$10\n0020\n00010000\n"
        self.assertEqual(expected, out)

    def test_help_tilde(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_tilde()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("~ <number>"))         

    # registers
   
    def test_registers_display_returns_to_prompt(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_registers('')
        out = stdout.getvalue()
        self.assertEqual('', out) 
    
    def test_registers_syntax_error_bad_format(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_registers('x')
        out = stdout.getvalue()
        self.assertEqual("Syntax error: x\n", out)         

    def test_registers_label_error_bad_value(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_registers('x=pony')
        out = stdout.getvalue()
        self.assertEqual("Label not found: pony\n", out)         

    def test_registers_invalid_register_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_registers('z=3')
        out = stdout.getvalue()
        self.assertEqual("Invalid register: z\n", out)         

    def test_registers_updates_single_register(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_registers('x=42')
        out = stdout.getvalue()
        self.assertEqual("", out)         
        self.assertEqual(0x42, mon._mpu.x)

    def test_registers_updates_all_registers(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_registers('a=42,x=43,y=44, sp=45, pc=4600')
        out = stdout.getvalue()
        self.assertEqual("", out)         
        self.assertEqual(0x42, mon._mpu.a)
        self.assertEqual(0x43, mon._mpu.x)
        self.assertEqual(0x44, mon._mpu.y)
        self.assertEqual(0x45, mon._mpu.sp)
        self.assertEqual(0x4600, mon._mpu.pc)

    def test_help_registers(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_registers()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("registers[<reg_name>"))         

    def test_do_add_label_syntax_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_add_label('should be label space value')
        out = stdout.getvalue()
        self.assertEqual("Syntax error: should be label space value\n", out)         

    def test_do_add_label_adds_label(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_add_label('$c000 foo')
        address_parser = mon._address_parser
        self.assertEqual(0xC000, address_parser.number('foo'))

    def test_help_add_label(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_add_label()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("add_label"))        

    def test_do_delete_label_no_args_displays_help(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_delete_label('')
        out = stdout.getvalue()
        self.assertTrue(out.startswith('delete_label'))

    def test_do_delete_label_with_bad_label_fails_silently(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_delete_label('non-existant-label')
        out = stdout.getvalue()
        self.assertEqual('', out)

    def test_do_delete_label_with_delete_label(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._address_parser.labels['foo'] = 0xc000
        mon.do_delete_label('foo') 
        self.assertFalse(mon._address_parser.labels.has_key('foo'))
        out = stdout.getvalue()
        self.assertEqual('', out)

    def test_show_labels_displays_labels(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._address_parser.labels = {'chrin': 0xffc4, 'chrout': 0xffd2}            
        mon.do_show_labels('')
        out = stdout.getvalue()
        self.assertEqual("ffc4: chrin\nffd2: chrout\n", out)        

    def test_help_show_labels(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._address_parser.labels = {'chrin': 0xffc4, 'chrout': 0xffd2}            
        mon.do_show_labels('')
        out = stdout.getvalue()
        self.assertEqual("ffc4: chrin\nffd2: chrout\n", out)        

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
