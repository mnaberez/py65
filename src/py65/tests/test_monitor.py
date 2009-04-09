import unittest
import sys
import re
import os
from py65.monitor import Monitor
from StringIO import StringIO

class MonitorTests(unittest.TestCase):

    # assemble
    
    def test_do_assemble_shows_help_for_invalid_args(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('c000')

        out = stdout.getvalue()
        self.assertTrue(out.startswith("assemble <address>"))

    def test_do_assemble_assembles_valid_statement(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('c000 lda #$ab')

        mpu = mon._mpu
        self.assertEqual(0xA9, mpu.memory[0xC000])
        self.assertEqual(0xAB, mpu.memory[0xC001])
    
    def test_do_assemble_outputs_disassembly(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('c000 lda #$ab')
        
        out = stdout.getvalue()
        self.assertEqual("$c000  a9 ab     LDA #$ab\n", out)

    def test_do_assemble_parses_start_address_label(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_add_label('c000 base')
        mon.do_assemble('c000 rts')
        
        mpu = mon._mpu
        self.assertEqual(0x60, mpu.memory[0xC000])

    def test_do_assemble_shows_bad_label_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('nonexistant rts')
        
        out = stdout.getvalue()
        self.assertEqual("Bad label: nonexistant\n", out)

    def test_do_assemble_shows_bad_statement_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('c000 foo')
        
        out = stdout.getvalue()
        self.assertEqual("Assemble failed: foo\n", out)

    def test_help_assemble(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_assemble()

        out = stdout.getvalue()
        self.assertTrue(out.startswith("assemble <address>"))

    # mpu

    def test_mpu_with_no_args_prints_current_lists_available_mpus(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_mpu('') 

        lines = stdout.getvalue().splitlines()
        self.assertEqual(2, len(lines))
        self.assertTrue(lines[0].startswith('Current MPU is '))
        self.assertTrue(lines[1].startswith('Available MPUs:'))

    def test_mpu_with_bad_arg_gives_error_lists_available_mpus(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_mpu('z80') 

        lines = stdout.getvalue().splitlines()
        self.assertEqual(2, len(lines))
        self.assertEqual('Unknown MPU: z80', lines[0])
        self.assertTrue(lines[1].startswith('Available MPUs:'))

    def test_mpu_selects_6502(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_mpu('6502') 

        lines = stdout.getvalue().splitlines()
        self.assertEqual(1, len(lines))
        self.assertEqual('Reset with new MPU 6502', lines[0])
        self.assertEqual('6502', mon._mpu.name)

    def test_mpu_selects_65C02(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_mpu('65C02') 

        lines = stdout.getvalue().splitlines()
        self.assertEqual(1, len(lines))
        self.assertEqual('Reset with new MPU 65C02', lines[0])
        self.assertEqual('65C02', mon._mpu.name)

    def test_help_mpu(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_mpu()  
        
        lines = stdout.getvalue().splitlines()    
        self.assertEqual("mpu\t\tPrint available microprocessors.", 
                         lines[0])
        self.assertEqual("mpu <type>\tSelect a new microprocessor.",
                         lines[1]) 

    # pwd

    def test_pwd_shows_os_getcwd(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_pwd()

        out = stdout.getvalue()
        self.assertEqual("%s\n" % os.getcwd(), out)
        

    def test_help_pwd(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_pwd()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("Show the current working"))
        
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
        old_name = mon._mpu.name
        mon.do_reset('')
        self.assertNotEqual(old_mpu, mon._mpu)
        self.assertEqual(old_name, mon._mpu.name)

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
