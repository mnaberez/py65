from py65.utils.addressing import AddressParser

class Disassembler:
    def __init__(self, mpu, address_parser=None):
        if address_parser is None:
            address_parser = AddressParser()

        self._mpu = mpu
        self._address_parser = address_parser

        self.addrWidth = mpu.addrWidth
        self.byteWidth = mpu.byteWidth
        self.addrFmt = mpu.addrFmt
        self.byteFmt = mpu.byteFmt
        self.addrMask = mpu.addrMask
        self.byteMask = mpu.byteMask

    def instruction_at(self, pc):
        """ Disassemble the instruction at PC and return a tuple
        containing (instruction byte count, human readable text)
        """

        instruction = self._mpu.ByteAt(pc)
        disasm, addressing = self._mpu.disassemble[instruction]

        if addressing == 'acc':
            disasm += ' A'
            length = 1

        elif addressing == 'abs':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address,
                '$' + self.addrFmt % address)
            disasm += ' ' + address_or_label
            length = 3

        elif addressing == 'abx':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address,
                '$' + self.addrFmt % address)
            disasm += ' %s,X' % address_or_label
            length = 3

        elif addressing == 'aby':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address,
                '$' + self.addrFmt % address)
            disasm += ' %s,Y' % address_or_label
            length = 3

        elif addressing == 'imm':
            byte = self._mpu.ByteAt(pc + 1)
            disasm += ' #$' + self.byteFmt % byte
            length = 2

        elif addressing == 'imp':
            length = 1

        elif addressing == 'ind':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address,
                '$' + self.addrFmt % address)
            disasm += ' (%s)' % address_or_label
            length = 3

        elif addressing == 'iny':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address,
                '$' + self.byteFmt % zp_address)
            disasm += ' (%s),Y' % address_or_label
            length = 2

        elif addressing == 'inx':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address,
                '$' + self.byteFmt % zp_address)
            disasm += ' (%s,X)' % address_or_label
            length = 2

        elif addressing == 'rel':
            opv = self._mpu.ByteAt(pc + 1)
            targ = pc + 2
            if opv & (1<<(self.byteWidth-1)):
                targ -= (opv ^ self.byteMask) + 1
            else:
                targ += opv
            targ &= self.addrMask

            address_or_label = self._address_parser.label_for(targ,
                '$' + self.addrFmt % targ)
            disasm += ' ' + address_or_label
            length = 2

        elif addressing == 'zpi':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address,
                '($' + self.byteFmt % zp_address + ')' )
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'zpg':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address,
                '$' + self.byteFmt % zp_address)
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing == 'zpx':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address,
                '$' + self.byteFmt % zp_address)
            disasm += ' %s,X' % address_or_label
            length = 2

        elif addressing == 'zpy':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address,
                '$' + self.byteFmt % zp_address)
            disasm += ' %s,Y' % address_or_label
            length = 2

        return (length, disasm)
