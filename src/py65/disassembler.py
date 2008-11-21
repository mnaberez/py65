class Disassembler:
    Instructions = [
        ['BRK','imp'], ['ORA','inx'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['ORA','zpg'], ['ASL','zpg'], ['???','imp'],
        ['PHP','imp'], ['ORA','imm'], ['ASL','acc'], ['???','imp'],
        ['???','imp'], ['ORA','abs'], ['ASL','abs'], ['???','imp'],
        ['BPL','rel'], ['ORA','iny'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['ORA','zpx'], ['ASL','zpx'], ['???','imp'],
        ['CLC','imp'], ['ORA','aby'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['ORA','abx'], ['ASL','abx'], ['???','imp'],
        ['JSR','abs'], ['AND','inx'], ['???','imp'], ['???','imp'],
        ['BIT','zpg'], ['AND','zpg'], ['ROL','zpg'], ['???','imp'],
        ['PLP','imp'], ['AND','imm'], ['ROL','acc'], ['???','imp'],
        ['BIT','abs'], ['AND','abs'], ['ROL','abs'], ['???','imp'],
        ['BMI','rel'], ['AND','iny'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['AND','zpx'], ['ROL','zpx'], ['???','imp'],
        ['SEC','imp'], ['AND','aby'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['AND','abx'], ['ROL','abx'], ['???','imp'],
        ['RTI','imp'], ['EOR','inx'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['EOR','zpg'], ['LSR','zpg'], ['???','imp'],
        ['PHA','imp'], ['EOR','imm'], ['LSR','acc'], ['???','imp'],
        ['JMP','abs'], ['EOR','abs'], ['LSR','abs'], ['???','imp'],
        ['BVC','rel'], ['EOR','iny'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['EOR','zpx'], ['LSR','zpx'], ['???','imp'],
        ['CLI','imp'], ['EOR','aby'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['EOR','abx'], ['LSR','abx'], ['???','imp'],
        ['RTS','imp'], ['ADC','inx'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['ADC','zpg'], ['ROR','zpg'], ['???','imp'],
        ['PLA','imp'], ['ADC','imm'], ['ROR','acc'], ['???','imp'],
        ['JMP','ind'], ['ADC','abs'], ['ROR','abs'], ['???','imp'],
        ['BVS','rel'], ['ADC','iny'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['ADC','zpx'], ['ROR','zpx'], ['???','imp'],
        ['SEI','imp'], ['ADC','aby'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['ADC','abx'], ['ROR','abx'], ['???','imp'],
        ['???','imp'], ['STA','inx'], ['???','imp'], ['???','imp'],
        ['STY','zpg'], ['STA','zpg'], ['STX','zpg'], ['???','imp'],
        ['DEY','imp'], ['???','imp'], ['TXA','imp'], ['???','imp'],
        ['STY','abs'], ['STA','abs'], ['STX','abs'], ['???','imp'],
        ['BCC','rel'], ['STA','iny'], ['???','imp'], ['???','imp'],
        ['STY','zpx'], ['STA','zpx'], ['STX','zpy'], ['???','imp'],
        ['TYA','imp'], ['STA','aby'], ['TXS','imp'], ['???','imp'],
        ['???','imp'], ['STA','abx'], ['???','imp'], ['???','imp'],
        ['LDY','imm'], ['LDA','inx'], ['LDX','imm'], ['???','imp'],
        ['LDY','zpg'], ['LDA','zpg'], ['LDX','zpg'], ['???','imp'],
        ['TAY','imp'], ['LDA','imm'], ['TAX','imp'], ['???','imp'],
        ['LDY','abs'], ['LDA','abs'], ['LDX','abs'], ['???','imp'],
        ['BCS','rel'], ['LDA','iny'], ['???','imp'], ['???','imp'],
        ['LDY','zpx'], ['LDA','zpx'], ['LDX','zpy'], ['???','imp'],
        ['CLV','imp'], ['LDA','aby'], ['TSX','imp'], ['???','imp'],
        ['LDY','abx'], ['LDA','abx'], ['LDX','aby'], ['???','imp'],
        ['CPY','imm'], ['CMP','inx'], ['???','imp'], ['???','imp'],
        ['CPY','zpg'], ['CMP','zpg'], ['DEC','zpg'], ['???','imp'],
        ['INY','imp'], ['CMP','imm'], ['DEX','imp'], ['???','imp'],
        ['CPY','abs'], ['CMP','abs'], ['DEC','abs'], ['???','imp'],
        ['BNE','rel'], ['CMP','iny'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['CMP','zpx'], ['DEC','zpx'], ['???','imp'],
        ['CLD','imp'], ['CMP','aby'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['CMP','abx'], ['DEC','abx'], ['???','imp'],
        ['CPX','imm'], ['SBC','inx'], ['???','imp'], ['???','imp'],
        ['CPX','zpg'], ['SBC','zpg'], ['INC','zpg'], ['???','imp'],
        ['INX','imp'], ['SBC','imm'], ['NOP','imp'], ['???','imp'],
        ['CPX','abs'], ['SBC','abs'], ['INC','abs'], ['???','imp'],
        ['BEQ','rel'], ['SBC','iny'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['SBC','zpx'], ['INC','zpx'], ['???','imp'],
        ['SED','imp'], ['SBC','aby'], ['???','imp'], ['???','imp'],
        ['???','imp'], ['SBC','abx'], ['INC','abx'], ['???','imp']
    ]

    def __init__(self, mpu, address_parser):
        self._mpu = mpu
        self._address_parser = address_parser

    def instruction_at(self, pc):
        """ Disassemble the instruction at PC and return a tuple
        containing (instruction byte count, human readable text)
        """

        instruction = self._mpu.ByteAt(pc)
        disasm, addressing = self.Instructions[instruction]

        if addressing == 'acc':
            disasm += ' A'
            length = 1

        elif addressing ==  'abs':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address, 
                '$%04x' % address)
            disasm += ' ' + address_or_label
            length = 3

        elif addressing ==  'abx':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address, 
                '$%04x' % address)
            disasm += ' %s,X' % address_or_label
            length = 3

        elif addressing ==  'aby':
            address = self._mpu.WordAt(pc + 1)
            address_or_label = self._address_parser.label_for(address, 
                '$%04x' % address)
            disasm += ' %s,Y' % address_or_label
            length = 3

        elif addressing == 'imm':
            byte = self._mpu.ByteAt(pc + 1)
            disasm += ' #$%02x' % byte
            length = 2

        elif addressing == 'imp':
            length = 1

        elif addressing == 'ind':
            address = self._mpu.WordAt(pc + 1)            
            address_or_label = self._address_parser.label_for(address, 
                '$%04x' % address)
            disasm += ' (%s)' % address_or_label
            length = 3

        elif addressing == 'iny':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' (%s),Y' % address_or_label
            length = 2

        elif addressing == 'inx':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' (%s,X)' % address_or_label
            length = 2

        elif addressing == 'rel':
            opv = self._mpu.ByteAt(pc + 1)
            targ = pc + 2
            if opv & 128:
                targ -= (opv ^ 255) + 1
            else:
                targ += opv
            targ &= 0xffff

            address_or_label = self._address_parser.label_for(targ, 
                '$%04x' % targ)
            disasm += ' ' + address_or_label
            length = 2

        elif addressing == 'zpg':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' %s' % address_or_label
            length = 2

        elif addressing ==  'zpx':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' %s,X' % address_or_label
            length = 2

        elif addressing ==  'zpy':
            zp_address = self._mpu.ByteAt(pc + 1)
            address_or_label = self._address_parser.label_for(zp_address, 
                '$%02x' % zp_address)
            disasm += ' %s,Y' % address_or_label
            length = 2        

        return (length, disasm)
