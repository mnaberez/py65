#!/usr/bin/env python -u

import cmd
import os
import re
import shlex
import asyncore
from py65.mpu6502 import MPU
from py65.util import itoa, AddressParser
from py65.memory import ObservableMemory

class Monitor(cmd.Cmd):

    def __init__(self, options={}, completekey='tab', stdin=None, stdout=None):
        self.options = options
        self._mpu = MPU()
        self._install_mpu_observers()
        self._update_prompt()
        self._address_parser = AddressParser()
        cmd.Cmd.__init__(self, completekey, stdin, stdout)

    def onecmd(self, line):
        line = self._preprocess_line(line)
        
        result = None
        try:
            result = cmd.Cmd.onecmd(self, line)
        except KeyboardInterrupt:
            self._output("Interrupt")
        except Exception,e:
            (file, fun, line), t, v, tbinfo = asyncore.compact_traceback()
            error = 'Error: %s, %s: file: %s line: %s' % (t, v, file, line)
            self._output(error)

        self._update_prompt()
        return result

    def _preprocess_line(self, line):
        # tilde command
        matches = re.match('^~\s*', line)
        if matches:
            start, end = matches.span()
            line = "tilde %s" % line[end:]

        # line comments
        quoted = False
        for pos in range(0, len(line)):
            if line[pos] in ('"', "'"):
                quoted = not quoted
            if (not quoted) and (line[pos] == ';'):
                line = line[:pos]
                break

        return line

    def _install_mpu_observers(self):
        def printit(operation, address, value):
            self.stdout.write(chr(value))

        m = ObservableMemory()
        m.subscribe(m.WRITE, [0xE001], printit)
        
        self._mpu.memory = m

    def _update_prompt(self):
        self.prompt = "\n%s\n." % repr(self._mpu)
        
    def _output(self, stuff):
        if stuff is not None:
            self.stdout.write(stuff + '\n')

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
        self._mpu = MPU()
        self._install_mpu_observers()
        
    def do_EOF(self, args):
        self._output('')
        return 1

    def help_EOF(self):
        self._output("To quit, type ^D or use the quit command.")

    def do_quit(self, args):
        return self.do_EOF
    
    def help_quit(self):
        return self.help_EOF()

    def help_step(self):
        self._output("Single-step through instructions.")

    def do_step(self, args):
        self._mpu.step()
    
    def help_return(self):
        self._output("Continues execution and returns to the monitor just")
        self._output("before the next RTS or RTI is executed.")
    
    def do_return(self, args):
        returns = [0x60, 0x40] # RTS, RTI
        self._run(stopcodes=returns)

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
            if register not in ('pc', 'sp', 'a', 'x', 'y'):
                self._output("Invalid register: %s" % register)
            else:
                try:
                    intval = self._address_parser.number(value) & 0xFFFF
                    if len(register) == 1:
                        intval &= 0xFF
                    setattr(self._mpu, register, intval)
                except ValueError:
                    self._output("Syntax error: %s" % value)
    
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
    
    def help_fill(self):
        self.output("fill <address_range> <data_list>")
        self.output("Fill memory in the specified address range with the data in")
        self.output("<data_list>.  If the size of the address range is greater")
        self.output("than the size of the data_list, the data_list is repeated.")
    
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

        out = itoa(start, 16).zfill(4) + ":  "
        for byte in self._mpu.memory[start:end+1]:
            out += "%02x  " % byte
        self._output(out)

    def do_add_label(self, args):
        split = shlex.split(args)
        if len(split) != 2:
            self._output("Syntax error: %s" % args)
            return
        
        address = self._address_parser.number(split[0])    
        label   = split[1]

        self._address_parser.labels[label] = address

    def do_show_labels(self, args):
        values = self._address_parser.labels.values()
        keys = self._address_parser.labels.keys()
      
        byaddress = zip(values, keys)
        byaddress.sort()
        for address, label in byaddress:
            self._output("%04x: %s" % (address, label))

    def do_delete_label(self, args):
        try:
            del self._address_parser.labels[args]
        except KeyError:
            pass



def main(args=None, options=None):
    c = Monitor(options)

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
