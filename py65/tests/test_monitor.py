import unittest
import sys
import os
import tempfile
from py65.monitor import Monitor

try:
    from StringIO import StringIO
except ImportError: # Python 3
    from io import StringIO


class MonitorTests(unittest.TestCase):

    # line processing

    def test__preprocess_line_removes_leading_dots_after_whitespace(self):
        mon = Monitor()
        self.assertEqual('help', mon._preprocess_line('  ...help'))

    def test__preprocess_line_removes_leading_and_trailing_whitespace(self):
        mon = Monitor()
        self.assertEqual('help', mon._preprocess_line(' \t help \t '))

    def test__preprocess_line_rewrites_shortcut_when_alone_on_line(self):
        mon = Monitor()
        self.assertEqual('assemble', mon._preprocess_line(' a'))

    def test__preprocess_line_rewrites_shortcut_with_arguments_on_line(self):
        mon = Monitor()
        self.assertEqual('assemble c000', mon._preprocess_line('a c000'))

    def test__preprocess_line_removes_semicolon_comments(self):
        mon = Monitor()
        self.assertEqual('assemble', mon._preprocess_line('a ;comment'))

    def test__preprocess_line_does_not_remove_semicolons_in_quotes(self):
        mon = Monitor()
        self.assertEqual('assemble lda #$";"',
                         mon._preprocess_line('a lda #$";" ;comment'))

    def test__preprocess_line_does_not_remove_semicolons_in_apostrophes(self):
        mon = Monitor()
        self.assertEqual("assemble lda #$';'",
                         mon._preprocess_line("assemble lda #$';' ;comment"))

    # add_label

    def test_shortcut_for_add_label(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('al')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('add_label'))

    def test_do_add_label_syntax_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_add_label('should be label space value')
        out = stdout.getvalue()
        err = "Syntax error: should be label space value\n"
        self.assertTrue(out.startswith(err))

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

    # assemble

    def test_shortcut_for_assemble(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('a')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('assemble'))

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
        self.assertEqual("Bad label: nonexistant rts\n", out)

    def test_do_assemble_shows_bad_syntax_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('c000 foo')

        out = stdout.getvalue()
        self.assertEqual("Syntax error: foo\n", out)

    def test_do_assemble_shows_overflow_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('c000 lda #$fff')

        out = stdout.getvalue()
        self.assertEqual("Overflow error: c000 lda #$fff\n", out)

    def test_do_assemble_passes_addr_for_relative_branch_calc(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble('4000 bvs $4005')

        out = stdout.getvalue()
        self.assertEqual("$4000  70 03     BVS $4005\n", out)

    def test_do_assemble_constrains_address_to_valid_range(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_assemble("-1 lda #$ab")

        out = stdout.getvalue()
        self.assertEqual("Overflow error: -1 lda #$ab\n", out)

    def test_help_assemble(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_assemble()

        out = stdout.getvalue()
        self.assertTrue("assemble <address>" in out)

    # cd

    def test_help_cd(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_cd()

        out = stdout.getvalue()
        self.assertTrue(out.startswith("cd <directory>"))

    def test_do_cd_with_no_dir_shows_help(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_cd("")

        out = stdout.getvalue()
        self.assertTrue(out.startswith("cd <directory>"))

    def test_do_cd_changes_cwd(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        here = os.path.abspath(os.path.dirname(__file__))
        mon.do_cd(here)

        out = stdout.getvalue()
        self.assertTrue(out.startswith(here))
        self.assertEqual(here, os.getcwd())

    def test_do_cd_with_bad_dir_shows_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_cd("/path/to/a/nonexistant/directory")

        out = stdout.getvalue()
        self.assertTrue(out.startswith("Cannot change directory"))

    # cycles

    def test_help_cycles(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_cycles()

        out = stdout.getvalue()
        self.assertTrue(out.startswith("Display the total number of cycles"))

    def test_do_cycles_shows_zero_initially(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_cycles("")

        out = stdout.getvalue()
        self.assertEqual(out, "0\n")

    def test_do_cycles_shows_count_after_step(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0x0000] = 0xEA  # => NOP (2 cycles)
        mon._mpu.step()
        mon.do_cycles("")

        out = stdout.getvalue()
        self.assertEqual(out, "2\n")

    # delete_label

    def test_shortcut_for_delete_label(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('dl')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('delete_label'))

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
        self.assertFalse('foo' in mon._address_parser.labels)
        out = stdout.getvalue()
        self.assertEqual('', out)

    # disassemble

    def test_shortcut_for_disassemble(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('d')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('disassemble'))

    def test_help_disassemble(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_disassemble()
        out = stdout.getvalue()
        self.assertTrue(out.startswith('disassemble <address_range>'))

    def test_disassemble_shows_help_when_given_extra_args(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_disassemble("c000 c001")
        out = stdout.getvalue()
        self.assertTrue(out.startswith('disassemble <address_range>'))

    def test_disassemble_will_disassemble_one_address(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0xEA  # => NOP
        mon._mpu.step()
        mon.do_disassemble("c000")

        out = stdout.getvalue()
        disasm = "$c000  ea        NOP\n"
        self.assertEqual(out, disasm)

    def test_disassemble_will_disassemble_an_address_range(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0xEA  # => NOP
        mon._mpu.memory[0xc001] = 0xEA  # => NOP
        mon._mpu.step()
        mon.do_disassemble("c000:c001")

        out = stdout.getvalue()
        disasm = "$c000  ea        NOP\n$c001  ea        NOP\n"
        self.assertEqual(out, disasm)

    def test_disassemble_wraps_an_instruction_around_memory(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xffff] = 0x20  # => JSR
        mon._mpu.memory[0x0000] = 0xD2  #
        mon._mpu.memory[0x0001] = 0xFF  # => $FFD2
        mon.do_disassemble("ffff")

        out = stdout.getvalue()
        disasm = "$ffff  20 d2 ff  JSR $ffd2\n"
        self.assertEqual(out, disasm)

    def test_disassemble_wraps_disassembly_list_around_memory(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xffff] = 0x20  # => JSR
        mon._mpu.memory[0x0000] = 0xD2
        mon._mpu.memory[0x0001] = 0xFF  # => $FFD2
        mon._mpu.memory[0x0002] = 0x20  # => JSR
        mon._mpu.memory[0x0003] = 0xE4
        mon._mpu.memory[0x0004] = 0xFF  # => $FFE4
        mon._mpu.memory[0x0005] = 0xEA  # => NOP
        mon.do_disassemble("ffff:5")
        out = stdout.getvalue()
        disasm = ("$ffff  20 d2 ff  JSR $ffd2\n"
                  "$0002  20 e4 ff  JSR $ffe4\n"
                  "$0005  ea        NOP\n")
        self.assertEqual(out, disasm)

    # fill

    def test_shortcut_f_for_fill(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('f')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('fill <address_range>'))

    def test_shortcut_gt_for_fill(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('>')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('fill <address_range>'))

    def test_help_fill(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_fill()

        out = stdout.getvalue()
        self.assertTrue(out.startswith('fill <address_range>'))

    def test_do_fill_with_no_args_shows_help(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_fill('')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('fill <address_range>'))

    def test_do_fill_will_fill_one_address(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0x00
        mon.do_fill('c000 aa')

        self.assertEqual(0xAA, mon._mpu.memory[0xc000])
        out = stdout.getvalue()
        self.assertTrue(out.startswith('Wrote +1 bytes from $c000 to $c000'))

    def test_do_fill_will_fill_an_address_range_with_a_single_byte(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0x00
        mon._mpu.memory[0xc001] = 0x00
        mon._mpu.memory[0xc002] = 0x00
        mon.do_fill('c000:c001 aa')

        self.assertEqual(0xAA, mon._mpu.memory[0xc000])
        self.assertEqual(0xAA, mon._mpu.memory[0xc001])
        self.assertEqual(0x00, mon._mpu.memory[0xc002])
        out = stdout.getvalue()
        self.assertTrue(out.startswith('Wrote +2 bytes from $c000 to $c001'))

    def test_do_fill_will_fill_an_address_range_with_byte_sequence(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xc000] = 0x00
        mon._mpu.memory[0xc001] = 0x00
        mon._mpu.memory[0xc002] = 0x00
        mon._mpu.memory[0xc003] = 0x00
        mon.do_fill('c000:c003 aa bb')

        self.assertEqual(0xAA, mon._mpu.memory[0xc000])
        self.assertEqual(0xBB, mon._mpu.memory[0xc001])
        self.assertEqual(0xAA, mon._mpu.memory[0xc002])
        self.assertEqual(0xBB, mon._mpu.memory[0xc003])
        out = stdout.getvalue()
        self.assertTrue(out.startswith('Wrote +4 bytes from $c000 to $c003'))

    # goto

    def test_shortcut_for_goto(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('g')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('goto'))

    def test_goto_without_args_shows_command_help(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.onecmd('goto')
        out = stdout.getvalue()
        self.assertTrue("goto <address>" in out)

    # help

    def test_help_without_args_shows_documented_commands(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.onecmd('help')
        out = stdout.getvalue()
        self.assertTrue("Documented commands" in out)

        stdout.truncate(0)
        mon.onecmd('h')
        out = stdout.getvalue()
        self.assertTrue("Documented commands" in out)

        stdout.truncate(0)
        mon.onecmd('?')
        out = stdout.getvalue()
        self.assertTrue("Documented commands" in out)

    def test_help_with_args_shows_command_help(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.onecmd('help assemble')
        out = stdout.getvalue()
        self.assertTrue("assemble <address>" in out)

        stdout.truncate(0)
        mon.onecmd('h a')
        out = stdout.getvalue()
        self.assertTrue("assemble <address>" in out)

    def test_help_with_invalid_args_shows_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.onecmd('help foo')
        out = stdout.getvalue()
        self.assertTrue(out.startswith("*** No help on foo"))

    # load

    def test_shortcut_for_load(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('l')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('load'))

    def test_load_with_more_than_two_args_syntax_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_load('one two three')
        out = stdout.getvalue()
        self.assertTrue(out.startswith('Syntax error'))

    def test_load(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)

        filename = tempfile.mktemp()
        try:
            f = open(filename, 'wb')
            f.write(b'\xaa\xbb\xcc')
            f.close()

            mon.do_load("'%s' a600" % filename)
            self.assertEqual('Wrote +3 bytes from $a600 to $a602\n',
                             stdout.getvalue())
            self.assertEqual([0xAA, 0xBB, 0xCC],
                             mon._mpu.memory[0xA600:0xA603])
        finally:
            os.unlink(filename)

    def test_help_load(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_load()
        out = stdout.getvalue()
        self.assertTrue(out.startswith('load'))

    # mem

    def test_shortcut_for_mem(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('m')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('mem <address_range>'))

    def test_do_mem_shows_help_when_given_no_args(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_mem('')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('mem <address_range>'))

    def test_do_mem_shows_help_when_given_extra_args(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_mem('c000 c001')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('mem <address_range>'))

    def test_do_mem_shows_memory_for_a_single_address(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xC000] = 0xAA
        mon.do_mem('c000')

        out = stdout.getvalue()
        self.assertEqual('c000:  aa\n', out)

    def test_do_mem_shows_memory_for_an_address_range(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0xC000] = 0xAA
        mon._mpu.memory[0xC001] = 0xBB
        mon._mpu.memory[0xC002] = 0xCC
        mon.do_mem('c000:c002')

        out = stdout.getvalue()
        self.assertEqual('c000:  aa  bb  cc\n', out)

    def test_do_mem_wraps_at_terminal_width(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._width = 14
        mon.do_mem('c000:c003')

        out = stdout.getvalue()
        self.assertEqual('c000:  00  00\n'
                         'c002:  00  00\n', out)

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

    def test_mpu_select_is_not_case_sensitive(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_mpu('65c02')
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

    # quit

    def test_shortcuts_for_quit(self):
        for shortcut in ["exit", "x", "q", "EOF"]:
            stdout = StringIO()
            mon = Monitor(stdout=stdout)
            mon.do_help(shortcut)

            out = stdout.getvalue()
            self.assertTrue(out.startswith('To quit'))

    def test_do_quit(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        exitnow = mon.do_quit('')
        self.assertEqual(True, exitnow)

    def test_help_quit(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_quit()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("To quit,"))

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

    # radix

    def test_shortcut_for_radix(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('rad')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('radix'))

    def test_help_radix(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_radix()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("radix [H|D|O|B]"))

    def test_radix_no_arg_displays_radix(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_radix('')
        out = stdout.getvalue()
        self.assertTrue(out.startswith("Default radix is Hexadecimal"))

    def test_radix_invalid_radix_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_radix('f')
        out = stdout.getvalue()
        self.assertTrue(out.startswith("Illegal radix: f"))

    def test_radix_sets_binary(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_radix('b')
        out = stdout.getvalue()
        self.assertTrue(out.startswith("Default radix is Binary"))

    def test_radix_sets_decimal(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_radix('d')
        out = stdout.getvalue()
        self.assertTrue(out.startswith("Default radix is Decimal"))

    def test_radix_sets_hexadecimal(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_radix('h')
        out = stdout.getvalue()
        self.assertTrue(out.startswith("Default radix is Hexadecimal"))

    def test_radix_sets_octal(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_radix('o')
        out = stdout.getvalue()
        self.assertTrue(out.startswith("Default radix is Octal"))

    # registers

    def test_shortcut_for_registers(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('r')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('registers'))

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
        mon.do_registers('a=42,x=43,y=44,p=45, sp=46, pc=4600')
        out = stdout.getvalue()
        self.assertEqual("", out)
        self.assertEqual(0x42, mon._mpu.a)
        self.assertEqual(0x43, mon._mpu.x)
        self.assertEqual(0x44, mon._mpu.y)
        self.assertEqual(0x45, mon._mpu.p)
        self.assertEqual(0x46, mon._mpu.sp)
        self.assertEqual(0x4600, mon._mpu.pc)

    def test_help_registers(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_registers()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("registers[<name>"))

    # return

    def test_shortcut_for_return(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('ret')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('return'))

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

    # save

    def test_shortcut_for_save(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('s')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('save'))

    def test_save_with_less_than_three_args_syntax_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_save('filename start')
        out = stdout.getvalue()
        self.assertTrue(out.startswith('Syntax error'))

    def test_save(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon._mpu.memory[0:3] = [0xAA, 0xBB, 0xCC]

        filename = tempfile.mktemp()
        try:
            mon.do_save("'%s' 0 2" % filename)
            self.assertEqual('Saved +3 bytes to %s\n' % filename,
                             stdout.getvalue())

            f = open(filename, 'rb')
            contents = f.read()
            f.close()
            self.assertEqual(b'\xaa\xbb\xcc', contents)
        finally:
            os.unlink(filename)

    def test_help_save(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_save()
        out = stdout.getvalue()
        self.assertTrue(out.startswith('save'))

    # step

    def test_shortcut_for_step(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('z')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('step'))

    # tilde

    def test_tilde_shortcut_with_space(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.onecmd('~ $10')
        out = stdout.getvalue()
        expected = "+16\n$10\n0020\n00010000\n"
        self.assertTrue(out.startswith(expected))

    def test_tilde_shortcut_without_space_for_vice_compatibility(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.onecmd('~$10')
        out = stdout.getvalue()
        expected = "+16\n$10\n0020\n00010000\n"
        self.assertTrue(out.startswith(expected))

    def test_do_tilde(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_tilde('$10')
        out = stdout.getvalue()
        expected = "+16\n$10\n0020\n00010000\n"
        self.assertTrue(out.startswith(expected))

    def test_do_tilde_with_no_arg_shows_help(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_tilde('')
        out = stdout.getvalue()
        expected = "~ <number>"
        self.assertTrue(out.startswith(expected))

    def test_do_tilde_with_bad_label_shows_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_tilde('bad_label')
        out = stdout.getvalue()
        expected = "Bad label: bad_label"
        self.assertTrue(out.startswith(expected))

    def test_do_tilde_with_overflow_shows_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_tilde('$FFFFFFFFFFFF')
        out = stdout.getvalue()
        expected = "Overflow error: $FFFFFFFFFFFF"
        self.assertTrue(out.startswith(expected))

    def test_help_tilde(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_tilde()
        out = stdout.getvalue()
        expected = "~ <number>"
        self.assertTrue(out.startswith(expected))

    # show_labels

    def test_shortcut_for_show_labels(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_help('shl')

        out = stdout.getvalue()
        self.assertTrue(out.startswith('show_labels'))

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

    # width

    def test_do_width_with_no_args_shows_current_width(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_width('')
        out = stdout.getvalue()
        self.assertEqual("Terminal width is 78\n", out)

    def test_do_width_with_arg_changes_width(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_width('38')
        out = stdout.getvalue()
        self.assertEqual("Terminal width is 38\n", out)

    def test_do_width_with_less_than_min_shows_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_width('3')
        out = stdout.getvalue()
        expected = "Minimum terminal width is 10\nTerminal width is 78\n"
        self.assertEqual(expected, out)

    def test_do_width_with_bad_arg_shows_error(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.do_width('bad')
        out = stdout.getvalue()
        expected = "Illegal width: bad\nTerminal width is 78\n"
        self.assertEqual(expected, out)

    def test_help_width(self):
        stdout = StringIO()
        mon = Monitor(stdout=stdout)
        mon.help_width()
        out = stdout.getvalue()
        self.assertTrue(out.startswith("width <columns>"))

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
