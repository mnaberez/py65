#!/usr/bin/env python -u

import cmd
import os
import re
import shlex
from mpu import MPU

class Monitor(cmd.Cmd):

    def __init__(self, options, completekey='tab', stdin=None, stdout=None):
        self.options = options
        self._mpu = MPU()
        self._update_prompt()
        self._radix = 16
        cmd.Cmd.__init__(self, completekey, stdin, stdout)

    def onecmd(self, line):
        matches = re.match('^~\s*', line)
        if matches:
            start, end = matches.span()
            line = "tilde %s" % line[end:]
        
        result = cmd.Cmd.onecmd(self, line)
        self._update_prompt()
        return result

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

    def do_reset(self):
        self._mpu = MPU()

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
        last_instruct = None
        while last_instruct != 0x60:  # RTS
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
                    self._radix = radix
                    changed = True
            if not changed:
                self._output("Illegal radix: %s" % args)

        for name, radix in radixes.iteritems():
            if self._radix == radix:
                self._output("Default radix is %s" % name)
    
    def help_tilde(self):
        self._output("~ <number>")
        self._output("Display the specified number in decimal, hex, octal, and binary.")
    
    def do_tilde(self, args):
        try:
            num = self._parsenum(args)
        except ValueError:
            self._output("Syntax error: %s" % args)
            return

        self._output("+%u" % num)
        self._output("$%02x" % num)
        self._output("%04o" % num)
        self._output(self._itoa(num, 2).zfill(8))
    
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
                    intval = self._parsenum(value) & 0xFFFF
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
            start = self._parsenum(split[1])
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

        address = start
        for byte in bytes:
            address &= 0xFFFF
            self._mpu.memory[address] = ord(byte)
            address += 1

        fmt = (address - start, start, address)
        self._output("Loaded %d bytes from %d to %d" % fmt)
    
    def help_fill(self):
        self.output("fill <address_range> <data_list>")
        self.output("Fill memory in the specified address range with the data in")
        self.output("<data_list>.  If the size of the address range is greater")
        self.output("than the size of the data_list, the data_list is repeated.")
    
    def do_fill(self, args):
        split = shlex.split(args)
        if len(split) != 2:
            self._output("Syntax error: %s" % args)
            return
        addresses, fillbyte = split

        start, end = self._parserange(addresses)
        fillbyte   = self._parsenum(fillbyte)
        
        self._fill(start, end, fillbyte)

    def _fill(self, start, end, byte):
        byte &= 0xFF
        address = start
        while address <= end:
            address &= 0xFFFF
            self._mpu.memory[address] = byte
            address += 1
        fmt = (end - start + 1, start, end)
        self._output("Filled +%d bytes from %d to %d" % fmt)
    
    def help_mem(self):
        self._output("mem <address_range>")
        self._output("Display the contents of memory.")
    
    def do_mem(self, args):
        start, end = self._parserange(args)

        out = self._itoa(start, 16) + ":  "
        for byte in self._mpu.memory[start:end]:
            out += "%02x  " % byte
        self._output(out)
         
    def _parsenum(self, num):
        if num.startswith('%'):
            return int(num[1:], 2)

        elif num.startswith('$'):
            return int(num[1:], 16)

        elif num.startswith('+'):
            return int(num[1:], 10)

        else:
            return int(num, self._radix)

    def _parserange(self, addresses):
        matches = re.match('^([^,]+)\s*[:,]+\s*([^,]+)$', addresses)
        if not matches:
            raise ValueError
        start, end = map(self._parsenum, matches.groups(0))

        if start > end:
            start, end = end, start            
        return (start, end)

    def _itoa(self, num, base=10):
       negative = num < 0
       if negative:
          num = -num
       digits = []
       while num > 0:
          num, last_digit = divmod(num, base)
          digits.append('0123456789abcdefghijklmnopqrstuvwxyz'[last_digit])
       if negative:
          digits.append('-')
       digits.reverse()
       return ''.join(digits) 

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
