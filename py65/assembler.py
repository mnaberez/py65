import re
from py65.utils.addressing import AddressParser


class Assembler:
    Statement = re.compile(r'^([A-z]{3}[0-7]?\s+'
                           r'\(?\s*)([^,\s\)]+)(\s*[,xXyY\s]*\)?'
                           r'[,xXyY\s]*)$')

    Addressing = (
        ('zpi', "($00FF)"),
        ('zpx', "$00FF,X"),
        ('zpy', "$00FF,Y"),
        ('zpg', "$00FF"),
        ('inx', "($00FF,X)"),
        ('iax', "($FFFF,X)"),
        ('iny', "($00FF),Y"),
        ('ind', "($FFFF)"),
        ('abx', "$FFFF,X"),
        ('aby', "$FFFF,Y"),
        ('abs', "$FFFF"),
        ('rel', "$FFFF"),
        ('imp', ""),
        ('acc', ""),
        ('acc', "A"),
        ('imm', "#$FF")
    )

    def __init__(self, mpu, address_parser=None):
        """ If a configured AddressParser is passed, symbolic addresses
        may be used in the assembly statements.
        """
        self._mpu = mpu

        if address_parser is None:
            address_parser = AddressParser()
        self._address_parser = address_parser

        self._addressing = []
        numchars = mpu.BYTE_WIDTH / 4  # 1 byte = 2 chars in hex
        for mode, format in self.Addressing:
            pat = "^" + re.escape(format) + "$"
            pat = pat.replace('00', '0{%d}' % numchars)
            pat = pat.replace('FF', '([0-9A-F]{%d})' % numchars)
            self._addressing.append([mode, re.compile(pat)])

    def assemble(self, statement, pc=0000):
        """ Assemble the given assembly language statement.  If the statement
        uses relative addressing, the program counter (pc) must also be given.
        The result is a list of bytes.  Raises when assembly fails.
        """
        opcode, operand = self.normalize_and_split(statement)

        for mode, pattern in self._addressing:
            match = pattern.match(operand)

            if match:
                # check if opcode supports this addressing mode
                try:
                    bytes = [self._mpu.disassemble.index((opcode, mode))]
                except ValueError:
                    continue

                operands = match.groups()

                if mode == 'rel':
                    # relative branch
                    absolute = int(''.join(operands), 16)
                    relative = (absolute - pc) - 2
                    relative = relative & self._mpu.byteMask
                    operands = [(self._mpu.BYTE_FORMAT % relative)]

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

            # target is an immediate value
            if target.startswith('#'):
                try:
                    if target[1] in ("'", '"'): # quoted ascii character
                        number = ord(target[2])
                    else:
                        number = self._address_parser.number(target[1:])
                except IndexError:
                    raise SyntaxError(statement)

                if (number < 0) or (number > self._mpu.byteMask):
                    raise OverflowError
                statement = before + '#$' + self._mpu.BYTE_FORMAT % number

            # target is the accumulator
            elif target in ('a', 'A'):
                pass

            # target is an address or label
            else:
                address = self._address_parser.number(target)
                statement = before + '$' + self._mpu.ADDR_FORMAT % address + after

        # separate opcode and operand
        splitted = statement.split(" ", 2)
        opcode = splitted[0].strip().upper()
        if len(splitted) > 1:
            operand = splitted[1].strip().upper()
        else:
            operand = ''
        return (opcode, operand)
