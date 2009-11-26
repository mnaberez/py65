#!/usr/bin/env python -u

import cmd
import os
import re
import shlex
import sys
from asyncore import compact_traceback
from py65.devices.mpu6502 import MPU as NMOS6502
from py65.devices.mpu65c02 import MPU as CMOS65C02
from py65.disassembler import Disassembler
from py65.assembler import Assembler
from py65.utils.addressing import AddressParser
from py65.utils import console
from py65.utils.conversions import itoa
from py65.memory import ObservableMemory

class Monitor(cmd.Cmd):

    def __init__(self, mpu_type=NMOS6502, completekey='tab', stdin=None, stdout=None):
        self._reset(mpu_type)
        self._width = 78
        self._update_prompt()
        self._add_shortcuts()
        cmd.Cmd.__init__(self, completekey, stdin, stdout)

    def onecmd(self, line):
        line = self._preprocess_line(line)
        
        result = None
        try:
            result = cmd.Cmd.onecmd(self, line)
        except KeyboardInterrupt:
            self._output("Interrupt")
        except Exception,e:
            (file, fun, line), t, v, tbinfo = compact_traceback()
            error = 'Error: %s, %s: file: %s line: %s' % (t, v, file, line)
            self._output(error)

        self._update_prompt()
        return result

    def _reset(self, mpu_type):
        self._mpu = mpu_type()
        self._install_mpu_observers()
        self._address_parser = AddressParser()
        self._disassembler = Disassembler(self._mpu, self._address_parser)
        self._assembler = Assembler(self._mpu, self._address_parser)

    def _add_shortcuts(self):
        self._shortcuts = {'~':   'tilde',
                           '?':   'help',
                           'a':   'assemble',
                           'al':  'add_label',
                           'd':   'disassemble',
                           'dl':  'delete_label',
                           'f':   'fill',
                           '>':   'fill',
                           'g':   'goto',
                           'l':   'load',
                           'm':   'mem',
                           'r':   'registers',
                           'ret': 'return',
                           'rad': 'radix',
                           's':   'save',
                           'shl': 'show_labels',
                           'x':   'quit',
                           'z':   'step'}

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
        for shortcut, command in self._shortcuts.iteritems():
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

        m = ObservableMemory()
        m.subscribe_to_write([0xF001], putc)
        m.subscribe_to_read([0xF004], getc)
        
        self._mpu.memory = m

    def _update_prompt(self):
        self.prompt = "\n%s\n." % repr(self._mpu)
        
    def _output(self, stuff):
        if stuff is not None:
            self.stdout.write(stuff + "\n")

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
        mpus = {'6502': NMOS6502, '65C02': CMOS65C02}
        
        def available_mpus():
            mpu_list = ', '.join(mpus.keys())
            self._output("Available MPUs: %s" % mpu_list)            
        
        if args == '':                      
            self._output("Current MPU is %s" % self._mpu.name)
            available_mpus()
        else:
            requested = args.upper()
            new_mpu = mpus.get(requested, None)
            if new_mpu is None:
                self._output("Unknown MPU: %s" % args)
                available_mpus()
            else:
                self._reset(new_mpu)
                self._output("Reset with new MPU %s" % self._mpu.name)

    def help_mpu(self):
        self._output("mpu\t\tPrint available microprocessors.")
        self._output("mpu <type>\tSelect a new microprocessor.")
        
    def do_EOF(self, args):
        self._output('')
        return 1

    def help_EOF(self):
        self._output("To quit, type ^D or use the quit command.")

    def do_quit(self, args):
        return self.do_EOF(args)
    
    def help_quit(self):
        return self.help_EOF()

    def do_assemble(self, args):
        split = args.split(None, 1)
        if len(split) != 2:
            return self._interactive_assemble(args)
        
        start, statement = split
        try:
            start = self._address_parser.number(start)
        except KeyError:
            self._output("Bad label: %s" % start)
            return

        bytes = self._assembler.assemble(statement, start)
        if bytes is None:
            self._output("Assemble failed: %s" % statement)
        else:
            end = start + len(bytes)
            self._mpu.memory[start:end] = bytes
            self.do_disassemble('%04x:%04x' % (start, end))

    def help_assemble(self):
        self._output("assemble <address> <statement>")
        self._output("Assemble a statement at the address.")

    def _interactive_assemble(self, args):
        if args == '':
          start = self._mpu.pc
        else:
          try:
              start = self._address_parser.number(args)
          except KeyError:
              self._output("Bad label: %s" % start)
              return
          
        assembling = True

        while assembling:
          prompt = "\r$%04x            " % (start)
          line = console.line_input(prompt, 
                    stdin=self.stdin, stdout=self.stdout)

          if not line:
            self.stdout.write("\n")
            return

          # assemble into memory
          bytes = self._assembler.assemble(line)
          if bytes is None:
              self.stdout.write("\r$%04x  ???\n" % start)
              continue
          end = start + len(bytes)
          self._mpu.memory[start:end] = bytes  

          # print disassembly
          bytes, disasm = self._disassembler.instruction_at(start)
          disassembly = self._format_disassembly(start, bytes, disasm)
          self.stdout.write("\r" + (' ' * (len(prompt+line) + 5) ) + "\r")
          self.stdout.write(disassembly + "\n")

          start += bytes

    def do_disassemble(self, args):
        start, end = self._address_parser.range(args)
        if start == end:
            end += 1
        
        address = start
        while address < end:
            bytes, disasm = self._disassembler.instruction_at(address)
            self._output(self._format_disassembly(address, bytes, disasm))                
            address += bytes
    
    def _format_disassembly(self, address, bytes, disasm):
        mem = ''
        for byte in self._mpu.memory[address:address+bytes]:
            mem += '%02x ' % byte
        
        return "$%04x  %-10s%s" % (address, mem, disasm)

    def help_disassemble(self):
        self._output("disassemble <address_range>")
        self._output("Disassemble instructions in the address range.")

    def help_step(self):
        self._output("step")
        self._output("Single-step through instructions.")

    def do_step(self, args):
        self._mpu.step()
        self.do_disassemble('%04x' % self._mpu.pc)
    
    def help_return(self):
        self._output("return")
        self._output("Continues execution and returns to the monitor just")
        self._output("before the next RTS or RTI is executed.")
    
    def do_return(self, args):
        returns = [0x60, 0x40] # RTS, RTI
        self._run(stopcodes=returns)

    def help_goto(self):
        self._output("goto <address>")
        self._output("Change the PC to address and continue execution.")

    def do_goto(self, args):
        self._mpu.pc = self._address_parser.number(args)
        brks = [0x00] # BRK
        self._run(stopcodes=brks)
    
    def _run(self, stopcodes=[]):
        last_instruct = None
        while last_instruct not in stopcodes:
            self._mpu.step()
            last_instruct = self._mpu.memory[self._mpu.pc]
    
    def help_radix(self):
        self._output("radix [H|D|O|B]")
        self._output("Set the default radix to hex, decimal, octal, or binary.")
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
            for name, radix in radixes.iteritems():
                if name[0].lower() == new:
                    self._address_parser.radix = radix
                    changed = True
            if not changed:
                self._output("Illegal radix: %s" % args)

        for name, radix in radixes.iteritems():
            if self._address_parser.radix == radix:
                self._output("Default radix is %s" % name)

    def help_tilde(self):
        self._output("~ <number>")
        self._output("Display the specified number in decimal, hex, octal, and binary.")
    
    def do_tilde(self, args):   
        try:
            num = self._address_parser.number(args)
        except ValueError:
            self._output("Syntax error: %s" % args)
            return

        self._output("+%u" % num)
        self._output("$%02x" % num)
        self._output("%04o" % num)
        self._output(itoa(num, 2).zfill(8))
    
    def help_registers(self):
        self._output("registers[<reg_name> = <number> [, <reg_name> = <number>]*]")
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
                    intval = self._address_parser.number(value) & 0xFFFF
                    if len(register) == 1:
                        intval &= 0xFF
                    setattr(self._mpu, register, intval)
                except KeyError, why:
                    self._output(why[0])
    
    def help_cd(self, args):
        self._output("cd <directory>")
        self._output("Change the working directory.")
    
    def do_cd(self, args):
        try:
            os.chdir(args)
        except OSError, why:
            msg = "Cannot change directory: [%d] %s" % (why[0], why[1])
            self._output(msg)
        self.do_pwd()

    def help_pwd(self):
        self._output("Show the current working directory.")
        
    def do_pwd(self, args=None):
        cwd = os.getcwd()
        self._output(cwd)

    def help_load(self):
        self._output("load \"filename\" <address>")
        self._output("Load the specified file into memory at the specified address.")
        self._output("Commodore-style load address bytes are ignored.")

    def do_load(self, args):
        split = shlex.split(args)
        if len(split) > 2:
            self._output("Syntax error: %s" % args)
            return

        filename = split[0]
        if len(split) == 2:
            start = self._address_parser.number(split[1])
        else:
            start = self._mpu.pc

        try:
            f = open(filename, 'rb')
            bytes = f.read()
            f.close()
        except (OSError, IOError), why:
            msg = "Cannot load file: [%d] %s" % (why[0], why[1])
            self._output(msg)
            return

        self._fill(start, start, map(ord, bytes))

    def do_save(self, args):
        split = shlex.split(args)
        if len(split) != 3:
            self._output("Syntax error: %s" % args)
            return
        
        filename = split[0]
        start = self._address_parser.number(split[1])
        end   = self._address_parser.number(split[2])
        
        bytes = self._mpu.memory[start:end+1]
        try:
            f = open(filename, 'wb')
            for byte in bytes:
                f.write(chr(byte))
            f.close()
        except (OSError, IOError), why:
            msg = "Cannot save file: [%d] %s" % (why[0], why[1])
            self._output(msg)
            return
        
        self._output("Saved +%d bytes to %s" % (len(bytes), filename))    

    def help_save(self):
        self._output("save \"filename\" <start> <end>")
        self._output("Save the specified memory range to disk as a binary file.")
        self._output("Commodore-style load address bytes are not written.")
    
    def help_fill(self):
        self._output("fill <address_range> <data_list>")
        self._output("Fill memory in the specified address range with the data in")
        self._output("<data_list>.  If the size of the address range is greater")
        self._output("than the size of the data_list, the data_list is repeated.")
    
    def do_fill(self, args):
        split = shlex.split(args)
        if len(split) < 2:
            self._output("Syntax error: %s" % args)
            return

        start, end = self._address_parser.range(split[0])
        filler = map(self._address_parser.number, split[1:])
        
        self._fill(start, end, filler)

    def _fill(self, start, end, filler):
        address = start
        length, index = len(filler), 0

        if start == end:
            end = start + length - 1
            if (end > 0xFFFF):
                end = 0xFFFF

        while address <= end:
            address &= 0xFFFF
            self._mpu.memory[address] = (filler[index] & 0xFF)
            index += 1
            if index == length:
                index = 0
            address += 1

        fmt = (end - start + 1, start, end)
        self._output("Wrote +%d bytes from $%04x to $%04x" % fmt)
    
    def help_mem(self):
        self._output("mem <address_range>")
        self._output("Display the contents of memory.")
    
    def do_mem(self, args):
        start, end = self._address_parser.range(args)

        line = "%04x:" % start
        for address in range(start, end+1):
            byte = self._mpu.memory[address]
            more = "  %02x" % byte                       
            
            exceeded = len(line) + len(more) > self._width
            if exceeded:
                self._output(line)
                line = "%04x:" % address
            line += more
        self._output(line)

    def help_add_label(self):
        self._output("add_label <address> <label>")
        self._output("Map a given address to a label.")

    def do_add_label(self, args):
        split = shlex.split(args)
        if len(split) != 2:
            self._output("Syntax error: %s" % args)
            return
        
        address = self._address_parser.number(split[0])    
        label   = split[1]

        self._address_parser.labels[label] = address

    def help_show_labels(self):
        self._output("show_labels")
        self._output("Display current label mappings.")

    def do_show_labels(self, args):
        values = self._address_parser.labels.values()
        keys = self._address_parser.labels.keys()
      
        byaddress = zip(values, keys)
        byaddress.sort()
        for address, label in byaddress:
            self._output("%04x: %s" % (address, label))

    def help_delete_label(self):
        self._output("delete_label <label>")
        self._output("Remove the specified label from the label tables.")

    def do_delete_label(self, args):
        if args == '':
            return self.help_delete_label()
        
        try:
            del self._address_parser.labels[args]
        except KeyError:
            pass

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
    except ImportError:
        pass

    try:
        c.onecmd('version')
        c.cmdloop()
    except KeyboardInterrupt:
        c._output('')
        pass

if __name__ == "__main__":
    main()
