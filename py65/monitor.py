#!/usr/bin/env python -u

"""py65mon -- interact with a simulated 6502-based system

Usage: %s [options]

Options:
-h, --help           : Show this message
-m, --mpu <device>   : Choose which MPU device (default is 6502)
-l, --load <file>    : Load a file at address 0
-r, --rom <file>     : Load a rom at the top of address space and reset into it
-g, --goto <address> : Perform a goto command after loading any files
"""

import cmd
import getopt
import os
import re
import shlex
import sys

from asyncore import compact_traceback
from py65.devices.mpu6502 import MPU as NMOS6502
from py65.devices.mpu65c02 import MPU as CMOS65C02
from py65.devices.mpu65org16 import MPU as V65Org16
from py65.disassembler import Disassembler
from py65.assembler import Assembler
from py65.utils.addressing import AddressParser
from py65.utils import console
from py65.utils.conversions import itoa
from py65.memory import ObservableMemory

try:
    from urllib2 import urlopen
except ImportError: # Python 3
    from urllib.request import urlopen

class Monitor(cmd.Cmd):

    Microprocessors = {'6502': NMOS6502, '65C02': CMOS65C02,
                       '65Org16': V65Org16}

    def __init__(self, mpu_type=NMOS6502, completekey='tab', stdin=None,
                 stdout=None, argv=None):
        self.mpu_type = mpu_type
        if argv is None:
            argv = sys.argv
        self._reset(self.mpu_type)
        self._width = 78
        self.prompt = "."
        self._add_shortcuts()
        cmd.Cmd.__init__(self, completekey, stdin, stdout)
        self._parse_args(argv)

    def _parse_args(self, argv):
        try:
            shortopts = 'hm:l:r:g:'
            longopts = ['help', 'mpu=', 'load=', 'rom=', 'goto=']
            options, args = getopt.getopt(argv[1:], shortopts, longopts)
        except getopt.GetoptError as exc:
            self._output(exc.args[0])
            self._usage()
            self._exit(1)

        for opt, value in options:
            if opt in ('-l', '--load'):
                cmd = "load %s" % value
                self.onecmd(cmd)

            if opt in ('-r', '--rom'):
                # load a ROM and run from the reset vector
                cmd = "load %s %d" % (value, -1)
                self.onecmd(cmd)
                physMask = self._mpu.memory.physMask
                reset = self._mpu.ResetTo & physMask
                dest = self._mpu.memory[reset] + \
                    (self._mpu.memory[reset + 1] << self.byteWidth)
                cmd = "goto %08x" % dest
                self.onecmd(cmd)

            if opt in ('-g', '--goto'):
                cmd = "goto %s" % value
                self.onecmd(cmd)

            if opt in ('-m', '--mpu'):
                if self._get_mpu(value) is None:
                    mpus = list(self.Microprocessors.keys())
                    mpus.sort()
                    msg = "Fatal: no such MPU. Available MPUs: %s"
                    self._output(msg % ', '.join(mpus))
                    sys.exit(1)
                cmd = "mpu %s" % value
                self.onecmd(cmd)

            elif opt in ("-h", "--help"):
                self._usage()
                self._exit(1)

    def _usage(self):
        usage = __doc__ % sys.argv[0]
        self._output(usage)

    def onecmd(self, line):
        line = self._preprocess_line(line)

        result = None
        try:
            result = cmd.Cmd.onecmd(self, line)
        except KeyboardInterrupt:
            self._output("Interrupt")
        except Exception:
            (file, fun, line), t, v, tbinfo = compact_traceback()
            error = 'Error: %s, %s: file: %s line: %s' % (t, v, file, line)
            self._output(error)

        if not line.startswith("quit"):
            self._output_mpu_status()

        return result

    def _reset(self, mpu_type):
        self._mpu = mpu_type()
        self.addrWidth = self._mpu.ADDR_WIDTH
        self.byteWidth = self._mpu.BYTE_WIDTH
        self.addrFmt = self._mpu.ADDR_FORMAT
        self.byteFmt = self._mpu.BYTE_FORMAT
        self.addrMask = self._mpu.addrMask
        self.byteMask = self._mpu.byteMask
        self._install_mpu_observers()
        self._address_parser = AddressParser()
        self._disassembler = Disassembler(self._mpu, self._address_parser)
        self._assembler = Assembler(self._mpu, self._address_parser)

    def _add_shortcuts(self):
        self._shortcuts = {'EOF':  'quit',
                           '~':    'tilde',
                           'a':    'assemble',
                           'al':   'add_label',
                           'd':    'disassemble',
                           'dl':   'delete_label',
                           'exit': 'quit',
                           'f':    'fill',
                           '>':    'fill',
                           'g':    'goto',
                           'h':    'help',
                           '?':    'help',
                           'l':    'load',
                           'm':    'mem',
                           'q':    'quit',
                           'r':    'registers',
                           'ret':  'return',
                           'rad':  'radix',
                           's':    'save',
                           'shl':  'show_labels',
                           'x':    'quit',
                           'z':    'step'}

    def _preprocess_line(self, line):
        # line comments
        quoted = False
        for pos, char in enumerate(line):
            if char in ('"', "'"):
                quoted = not quoted
            if (not quoted) and (char == ';'):
                line = line[:pos]
                break

        # whitespace & leading dots
        line = line.strip(' \t').lstrip('.')

        # special case for vice compatibility
        if line.startswith('~'):
            line = self._shortcuts['~'] + ' ' + line[1:]

        # command shortcuts
        for shortcut, command in self._shortcuts.items():
            if line == shortcut:
                line = command
                break

            pattern = '^%s\s+' % re.escape(shortcut)
            matches = re.match(pattern, line)
            if matches:
                start, end = matches.span()
                line = "%s %s" % (command, line[end:])
                break

        return line

    def _get_mpu(self, name):
        requested = name.lower()
        mpu = None
        for key, klass in self.Microprocessors.items():
            if key.lower() == requested:
                mpu = klass
                break
        return mpu

    def _install_mpu_observers(self):
        def putc(address, value):
            self.stdout.write(chr(value))
            self.stdout.flush()

        def getc(address):
            char = console.getch_noblock(self.stdin)
            if char:
                byte = ord(char)
            else:
                byte = 0
            return byte

        m = ObservableMemory(addrWidth=self.addrWidth)
        m.subscribe_to_write([0xF001], putc)
        m.subscribe_to_read([0xF004], getc)

        self._mpu.memory = m

    def _output_mpu_status(self):
        self._output("\n" + repr(self._mpu))

    def _output(self, stuff):
        if stuff is not None:
            self.stdout.write(stuff + "\n")

    def _exit(self, exitcode=0):
        sys.exit(exitcode)

    def do_help(self, args):
        args = self._shortcuts.get(args.strip(), args)
        return cmd.Cmd.do_help(self, args)

    def help_version(self):
        self._output("version\t\tDisplay Py65 version information.")

    def do_version(self, args):
        self._output("\nPy65 Monitor")

    def help_help(self):
        self._output("help\t\tPrint a list of available actions.")
        self._output("help <action>\tPrint help for <action>.")

    def help_reset(self):
        self._output("reset\t\tReset the microprocessor")

    def do_reset(self, args):
        klass = self._mpu.__class__
        self._reset(mpu_type=klass)

    def do_mpu(self, args):
        def available_mpus():
            mpus = list(self.Microprocessors.keys())
            mpus.sort()
            self._output("Available MPUs: %s" % ', '.join(mpus))

        if args == '':
            self._output("Current MPU is %s" % self._mpu.name)
            available_mpus()
        else:
            new_mpu = self._get_mpu(args)
            if new_mpu is None:
                self._output("Unknown MPU: %s" % args)
                available_mpus()
            else:
                self._reset(new_mpu)
                self._output("Reset with new MPU %s" % self._mpu.name)

    def help_mpu(self):
        self._output("mpu\t\tPrint available microprocessors.")
        self._output("mpu <type>\tSelect a new microprocessor.")

    def do_quit(self, args):
        self._output('')
        return 1

    def help_quit(self):
        self._output("To quit, type ^D or use the quit command.")

    def do_assemble(self, args):
        splitted = args.split(None, 1)
        if len(splitted) != 2:
            return self._interactive_assemble(args)

        statement = splitted[1]
        try:
            start = self._address_parser.number(splitted[0])
            bytes = self._assembler.assemble(statement, start)
            end = start + len(bytes)
            self._mpu.memory[start:end] = bytes
            self.do_disassemble(self.addrFmt % start)
        except KeyError:
            self._output("Bad label: %s" % args)
        except OverflowError:
            self._output("Overflow error: %s" % args)
        except SyntaxError:
            self._output("Syntax error: %s" % statement)

    def help_assemble(self):
        self._output("assemble\t\t\t"
                     "Start interactive assembly at the program counter.")
        self._output("assemble <address>\t\t"
                     "Start interactive assembly at the address.")
        self._output("assemble <address> <statement>\t"
                     "Assemble a statement at the address.")

    def _interactive_assemble(self, args):
        if args == '':
            start = self._mpu.pc
        else:
            try:
                start = self._address_parser.number(args)
            except KeyError:
                self._output("Bad label: %s" % args)
                return

        while True:
            prompt = "\r$" + (self.addrFmt % start) + "   " + \
                (" " * int(1 + self.byteWidth / 4) * 3)

            line = console.line_input(prompt,
                                      stdin=self.stdin, stdout=self.stdout)

            if not line.strip():
                self.stdout.write("\n")
                return

            # assemble into memory
            try:
                bytes = self._assembler.assemble(line, pc=start)
                numbytes = len(bytes)

                end = start + numbytes
                self._mpu.memory[start:end] = bytes

                # print disassembly
                _, disasm = self._disassembler.instruction_at(start)
                fdisasm = self._format_disassembly(start, numbytes, disasm)
                indent = ' ' * (len(prompt + line) + 5)
                self.stdout.write("\r" + indent + "\r")
                self.stdout.write(fdisasm + "\n")

                # advance to next address
                start += numbytes
                if start >= (2 ** self._mpu.ADDR_WIDTH):
                    start = 0
            except KeyError:
                addr = self.addrFmt % start
                self.stdout.write("\r$%s  ?Label\n" % addr)
            except OverflowError:
                addr = self.addrFmt % start
                self.stdout.write("\r$%s  ?Overflow\n" % addr)
            except SyntaxError:
                addr = self.addrFmt % start
                self.stdout.write("\r$%s  ?Syntax\n" % addr)

    def do_disassemble(self, args):
        splitted = shlex.split(args)
        if len(splitted) != 1:
            return self.help_disassemble()

        address_parts = splitted[0].split(":")
        start = self._address_parser.number(address_parts[0])
        if len(address_parts) > 1:
            end = self._address_parser.number(address_parts[1])
        else:
            end = start

        max_address = (2 ** self._mpu.ADDR_WIDTH) - 1
        cur_address = start
        needs_wrap = start > end

        while needs_wrap or cur_address <= end:
            length, disasm = self._disassembler.instruction_at(cur_address)
            self._output(self._format_disassembly(cur_address, length, disasm))

            remaining = length
            while remaining:
                remaining -= 1
                cur_address += 1
                if start > end and cur_address > max_address:
                    needs_wrap = False
                    cur_address = 0

    def _format_disassembly(self, address, length, disasm):
        cur_address = address
        max_address = (2 ** self._mpu.ADDR_WIDTH) - 1

        bytes_remaining = length
        dump = ''

        while bytes_remaining:
            if cur_address > max_address:
                cur_address = 0
            dump += self.byteFmt % self._mpu.memory[cur_address] + " "
            cur_address += 1
            bytes_remaining -= 1

        fieldwidth = 1 + int(1 + self.byteWidth / 4) * 3
        fieldfmt = "%%-%ds" % fieldwidth
        return "$" + self.addrFmt % address + "  " + fieldfmt % dump + disasm

    def help_disassemble(self):
        self._output("disassemble <address_range>")
        self._output("Disassemble instructions in the address range.")
        self._output('Range is specified like "<start>:<end>".')

    def help_step(self):
        self._output("step")
        self._output("Single-step through instructions.")

    def do_step(self, args):
        self._mpu.step()
        self.do_disassemble(self.addrFmt % self._mpu.pc)

    def help_return(self):
        self._output("return")
        self._output("Continues execution and returns to the monitor just")
        self._output("before the next RTS or RTI is executed.")

    def do_return(self, args):
        returns = [0x60, 0x40]  # RTS, RTI
        self._run(stopcodes=returns)

    def help_goto(self):
        self._output("goto <address>")
        self._output("Change the PC to address and continue execution.")

    def do_goto(self, args):
        if args == '':
            return self.help_goto()

        self._mpu.pc = self._address_parser.number(args)
        brks = [0x00]  # BRK
        self._run(stopcodes=brks)

    def _run(self, stopcodes=[]):
        last_instruct = None
        while last_instruct not in stopcodes:
            self._mpu.step()
            last_instruct = self._mpu.memory[self._mpu.pc]

    def help_radix(self):
        self._output("radix [H|D|O|B]")
        self._output("Set default radix to hex, decimal, octal, or binary.")
        self._output("With no argument, the current radix is printed.")

    def help_cycles(self):
        self._output("Display the total number of cycles executed.")

    def do_cycles(self, args):
        self._output(str(self._mpu.processorCycles))

    def do_radix(self, args):
        radixes = {'Hexadecimal': 16, 'Decimal': 10, 'Octal': 8, 'Binary': 2}

        if args != '':
            new = args[0].lower()
            changed = False
            for name, radix in radixes.items():
                if name[0].lower() == new:
                    self._address_parser.radix = radix
                    changed = True
            if not changed:
                self._output("Illegal radix: %s" % args)

        for name, radix in radixes.items():
            if self._address_parser.radix == radix:
                self._output("Default radix is %s" % name)

    def help_tilde(self):
        self._output("~ <number>")
        self._output("Display a number in decimal, hex, octal, and binary.")

    def do_tilde(self, args):
        if args == '':
            return self.help_tilde()

        try:
            num = self._address_parser.number(args)
            self._output("+%u" % num)
            self._output("$" + self.byteFmt % num)
            self._output("%04o" % num)
            self._output(itoa(num, 2).zfill(8))
        except KeyError:
            self._output("Bad label: %s" % args)
        except OverflowError:
            self._output("Overflow error: %s" % args)

    def help_registers(self):
        self._output("registers[<name>=<value> [, <name>=<value>]*]")
        self._output("Assign respective registers.  With no parameters,")
        self._output("display register values.")

    def do_registers(self, args):
        if args == '':
            return

        pairs = re.findall('([^=,\s]*)=([^=,\s]*)', args)
        if pairs == []:
            return self._output("Syntax error: %s" % args)

        for register, value in pairs:
            if register not in ('pc', 'sp', 'a', 'x', 'y', 'p'):
                self._output("Invalid register: %s" % register)
            else:
                try:
                    intval = self._address_parser.number(value) & self.addrMask
                    if len(register) == 1:
                        intval &= self.byteMask
                    setattr(self._mpu, register, intval)
                except KeyError as exc:
                    self._output(exc.args[0])

    def help_cd(self):
        self._output("cd <directory>")
        self._output("Change the working directory.")

    def do_cd(self, args):
        if args == '':
            return self.help_cd()

        try:
            os.chdir(args)
        except OSError as exc:
            msg = "Cannot change directory: [%d] %s" % (exc.errno,
                exc.strerror)
            self._output(msg)
        self.do_pwd()

    def help_pwd(self):
        self._output("Show the current working directory.")

    def do_pwd(self, args=None):
        cwd = os.getcwd()
        self._output(cwd)

    def help_load(self):
        self._output("load \"filename\" <address>")
        self._output("Load a file into memory at the specified address.")
        self._output("Commodore-style load address bytes are ignored.")

    def do_load(self, args):
        split = shlex.split(args)
        if len(split) > 2:
            self._output("Syntax error: %s" % args)
            return

        filename = split[0]

        if "://" in filename:
            try:
                f = urlopen(filename)
                bytes = f.read()
                f.close()
            except Exception as exc:
                msg = "Cannot fetch remote file: %s" % str(exc)
                self._output(msg)
                return
        else:
            try:
                f = open(filename, 'rb')
                bytes = f.read()
                f.close()
            except (OSError, IOError) as exc:
                msg = "Cannot load file: [%d] %s" % (exc.errno, exc.strerror)
                self._output(msg)
                return

        if len(split) == 2:
            if split[1] == "-1":
                # load a ROM to top of memory
                start = self.addrMask - len(bytes) / int(self.byteWidth / 8) + 1
            else:
                start = self._address_parser.number(split[1])
        else:
            start = self._mpu.pc

        if self.byteWidth == 8:
            if isinstance(bytes, str):
                bytes = map(ord, bytes)
            else: # Python 3
                bytes = [ b for b in bytes ]

        elif self.byteWidth == 16:
            def format(msb, lsb):
                if isinstance(bytes, str):
                    return (ord(msb) << 8) + ord(lsb)
                else: # Python 3
                    return (msb << 8) + lsb
            bytes = list(map(format, bytes[0::2], bytes[1::2]))

        self._fill(start, start, bytes)

    def do_save(self, args):
        split = shlex.split(args)
        if len(split) != 3:
            self._output("Syntax error: %s" % args)
            return

        filename = split[0]
        start = self._address_parser.number(split[1])
        end = self._address_parser.number(split[2])

        mem = self._mpu.memory[start:end + 1]
        try:
            f = open(filename, 'wb')
            for m in mem:
                # output each octect from msb first
                for shift in range(self.byteWidth - 8, -1, -8):
                    f.write(bytearray([(m >> shift) & 0xff]))
            f.close()
        except (OSError, IOError) as exc:
            msg = "Cannot save file: [%d] %s" % (exc.errno, exc.strerror)
            self._output(msg)
            return

        self._output("Saved +%d bytes to %s" % (len(mem), filename))

    def help_save(self):
        self._output("save \"filename\" <start> <end>")
        self._output("Save the specified memory range as a binary file.")
        self._output("Commodore-style load address bytes are not written.")

    def help_fill(self):
        self._output("fill <address_range> <data_list>")
        self._output("Fill memory in the address range with the data in")
        self._output("<data_list>.  If the size of the address range is")
        self._output("greater than the size of the data_list, the data_list ")
        self._output("is repeated.")

    def do_fill(self, args):
        split = shlex.split(args)
        if len(split) < 2:
            return self.help_fill()

        start, end = self._address_parser.range(split[0])
        filler = list(map(self._address_parser.number, split[1:]))

        self._fill(start, end, filler)

    def _fill(self, start, end, filler):
        address = start
        length, index = len(filler), 0

        if start == end:
            end = start + length - 1
            if (end > self.addrMask):
                end = self.addrMask

        while address <= end:
            address &= self.addrMask
            self._mpu.memory[address] = (filler[index] & self.byteMask)
            index += 1
            if index == length:
                index = 0
            address += 1

        fmt = (end - start + 1, start, end)
        starttoend = "$" + self.addrFmt + " to $" + self.addrFmt
        self._output(("Wrote +%d bytes from " + starttoend) % fmt)

    def help_mem(self):
        self._output("mem <address_range>")
        self._output("Display the contents of memory.")
        self._output('Range is specified like "<start:end>".')

    def do_mem(self, args):
        split = shlex.split(args)
        if len(split) != 1:
            return self.help_mem()

        start, end = self._address_parser.range(split[0])

        line = self.addrFmt % start + ":"
        for address in range(start, end + 1):
            byte = self._mpu.memory[address]
            more = "  " + self.byteFmt % byte

            exceeded = len(line) + len(more) > self._width
            if exceeded:
                self._output(line)
                line = self.addrFmt % address + ":"
            line += more
        self._output(line)

    def help_add_label(self):
        self._output("add_label <address> <label>")
        self._output("Map a given address to a label.")

    def do_add_label(self, args):
        split = shlex.split(args)
        if len(split) != 2:
            self._output("Syntax error: %s" % args)
            return self.help_add_label()

        address = self._address_parser.number(split[0])
        label = split[1]

        self._address_parser.labels[label] = address

    def help_show_labels(self):
        self._output("show_labels")
        self._output("Display current label mappings.")

    def do_show_labels(self, args):
        values = list(self._address_parser.labels.values())
        keys = list(self._address_parser.labels.keys())

        byaddress = list(zip(values, keys))
        byaddress.sort()
        for address, label in byaddress:
            self._output(self.addrFmt % address + ": " + label)

    def help_delete_label(self):
        self._output("delete_label <label>")
        self._output("Remove the specified label from the label tables.")

    def do_delete_label(self, args):
        if args == '':
            return self.help_delete_label()

        if args in self._address_parser.labels:
            del self._address_parser.labels[args]

    def do_width(self, args):
        if args != '':
            try:
                new_width = int(args)
                if new_width >= 10:
                    self._width = new_width
                else:
                    self._output("Minimum terminal width is 10")
            except ValueError:
                self._output("Illegal width: %s" % args)

        self._output("Terminal width is %d" % self._width)

    def help_width(self):
        self._output("width <columns>")
        self._output("Set the width used by some commands to wrap output.")
        self._output("With no argument, the current width is printed.")


def main(args=None):
    c = Monitor()

    try:
        import readline
        readline = readline  # pyflakes
    except ImportError:
        pass

    try:
        c.onecmd('version')
        c.cmdloop()
    except KeyboardInterrupt:
        c._output('')

if __name__ == "__main__":
    main()
