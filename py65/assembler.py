import re
from py65.utils.addressing import AddressParser


class Assembler:
    Statement = re.compile(r'^([A-z]{3}[0-7]?\s+'
                           r'\(?\s*)([^,\s\)]+)(\s*[,xXyY\s]*\)?'
                           r'[,xXyY\s]*)$')

    Addressing8 = [
        ['zpi',  # "($0012)"
         re.compile(r'^\(\$00([0-9A-F]{2})\)$')],
        ['zpx',  # "$0012,X"
         re.compile(r'^\$00([0-9A-F]{2}),X$')],
        ['zpy',  # "$0012,Y"
         re.compile(r'^\$00([0-9A-F]{2}),Y$')],
        ['zpg',  # "$0012"
         re.compile(r'^\$00([0-9A-F]{2})$')],
        ['inx',  # "($0012,X)
         re.compile(r'^\(\$00([0-9A-F]{2}),X\)$')],
        ['iax',  # "($1234,X)
         re.compile(r'^\(\$([0-9A-F]{2})([0-9A-F]{2}),X\)$')],
        ['iny',  # "($0012),Y"
         re.compile(r'^\(\$00([0-9A-F]{2})\),Y$')],
        ['ind',  # "($1234)"
         re.compile(r'^\(\$([0-9A-F]{2})([0-9A-F]{2})\)$')],
        ['abx',  # "$1234,X"
         re.compile(r'^\$([0-9A-F]{2})([0-9A-F]{2}),X$')],
        ['aby',  # "$1234,Y"
         re.compile(r'^\$([0-9A-F]{2})([0-9A-F]{2}),Y$')],
        ['abs',  # "$1234"
         re.compile(r'^\$([0-9A-F]{2})([0-9A-F]{2})$')],
        ['rel',  # "$1234"
         re.compile(r'^\$([0-9A-F]{2})([0-9A-F]{2})$')],
        ['imp',  # ""
         re.compile(r'^$')],
        ['acc',  # ""
         re.compile(r'^$')],
        ['acc',  # "A"
         re.compile(r'^A$')],
        ['imm',  # "#$12"
         re.compile(r'^#\$([0-9A-F]{2})$')]
    ]

    Addressing16 = [
        ['zpi',  # "($00001234)"
         re.compile(r'^\(\$0000([0-9A-F]{4})\)$')],
        ['zpx',  # "$00001234,X"
         re.compile(r'^\$0000([0-9A-F]{4}),X$')],
        ['zpy',  # "$00001234,Y"
         re.compile(r'^\$0000([0-9A-F]{4}),Y$')],
        ['zpg',  # "$00001234"
         re.compile(r'^\$0000([0-9A-F]{4})$')],
        ['inx',  # "($00001234,X)"
         re.compile(r'^\(\$0000([0-9A-F]{4}),X\)$')],
        ['iny',  # "($00001234),Y"
         re.compile(r'^\(\$0000([0-9A-F]{4})\),Y$')],
        ['ind',  # "($12345678)"
         re.compile(r'^\(\$([0-9A-F]{4})([0-9A-F]{4})\)$')],
        ['abx',  # "$12345678,X"
         re.compile(r'^\$([0-9A-F]{4})([0-9A-F]{4}),X$')],
        ['aby',  # "$12345678,Y"
         re.compile(r'^\$([0-9A-F]{4})([0-9A-F]{4}),Y$')],
        ['abs',  # "$12345678"
         re.compile(r'^\$([0-9A-F]{4})([0-9A-F]{4})$')],
        ['rel',  # "$12345678"
         re.compile(r'^\$([0-9A-F]{4})([0-9A-F]{4})$')],
        ['imp',  # ""
         re.compile(r'^$')],
        ['acc',  # ""
         re.compile(r'^$')],
        ['acc',  # "A"
         re.compile(r'^A$')],
        ['imm',  # "#$1234"
         re.compile(r'^#\$([0-9A-F]{4})$')]
    ]
    Addressing = Addressing8

    def __init__(self, mpu, address_parser=None):
        """ If a configured AddressParser is passed, symbolic addresses
        may be used in the assembly statements.
        """
        if address_parser is None:
            address_parser = AddressParser()

        self._mpu = mpu
        self._address_parser = address_parser

        self.addrWidth = mpu.ADDR_WIDTH
        self.byteWidth = mpu.BYTE_WIDTH
        self.addrFmt = mpu.ADDR_FORMAT
        self.byteFmt = mpu.BYTE_FORMAT
        self.addrMask = mpu.addrMask
        self.byteMask = mpu.byteMask

        if self.byteWidth == 8:
            self.Addressing = self.Addressing8
        else:
            self.Addressing = self.Addressing16

    def assemble(self, statement, pc=0000):
        """ Assemble the given assembly language statement.  If the statement
        uses relative addressing, the program counter (pc) must also be given.
        The result is a list of bytes.  Raises when assembly fails.
        """
        opcode, operand = self.normalize_and_split(statement)

        for mode, pattern in self.Addressing:
            match = pattern.match(operand)

            if match:
                try:
                    bytes = [self._mpu.disassemble.index((opcode, mode))]
                except ValueError:
                    continue

                operands = match.groups()

                if mode == 'rel':
                    # relative branch
                    absolute = int(''.join(operands), 16)
                    relative = (absolute - pc) - 2
                    relative = relative & self.byteMask
                    operands = [(self.byteFmt % relative)]

                elif len(operands) == 2:
                    # swap bytes
                    operands = (operands[1], operands[0])

                operands = [int(hex, 16) for hex in operands]
                bytes.extend(operands)

                # raise if the assembled bytes would exceed top of memory
                if (pc + len(bytes)) > (2 ** self._mpu.ADDR_WIDTH):
                    raise OverflowError

                return bytes

        # assembly failed
        raise SyntaxError(statement)

    def normalize_and_split(self, statement):
        """ Given an assembly language statement like "lda $c12,x", normalize
            the statement by uppercasing it, removing unnecessary whitespace,
            and parsing the address part using AddressParser.  The result of
            the normalization is a tuple of two strings (opcode, operand).
        """
        statement = ' '.join(str.split(statement))

        # normalize target in operand
        match = self.Statement.match(statement)
        if match:
            before, target, after = match.groups()

            # target is an immediate number
            if target.startswith('#'):
                number = self._address_parser.number(target[1:])
                if (number < 0x00) or (number > self.byteMask):
                    raise OverflowError
                statement = before + '#$' + self.byteFmt % number

            # target is the accumulator
            elif target in ('a', 'A'):
                pass

            # target is an address or label
            else:
                address = self._address_parser.number(target)
                statement = before + '$' + self.addrFmt % address + after

        # separate opcode and operand
        splitted = statement.split(" ", 2)
        opcode = splitted[0].strip().upper()
        if len(splitted) > 1:
            operand = splitted[1].strip().upper()
        else:
            operand = ''
        return (opcode, operand)
