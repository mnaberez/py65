from py65.devices import mpu6502
from py65.utils.devices import make_instruction_decorator


class MPU(mpu6502.MPU):
    def __init__(self, *args, **kwargs):
        mpu6502.MPU.__init__(self, *args, **kwargs)
        self.name = '65C02'
        self.waiting = False

    def step(self, trace=False):
        if self.waiting:
            self.processorCycles += 1
        else:
            mpu6502.MPU.step(self, trace)
        return self

    # Make copies of the lists
    instruct = mpu6502.MPU.instruct[:]
    cycletime = mpu6502.MPU.cycletime[:]
    extracycles = mpu6502.MPU.extracycles[:]
    disassemble = mpu6502.MPU.disassemble[:]

    instruction = make_instruction_decorator(instruct, disassemble,
                                             cycletime, extracycles)

    # addressing modes

    def ZeroPageIndirectAddr(self):
        return self.WordAt(255 & (self.ByteAt(self.pc)))

    def IndirectAbsXAddr(self):
        return (self.WordAt(self.pc) + self.x) & self.addrMask

    # operations

    def opRMB(self, x, mask):
        address = x()
        self.memory[address] &= mask

    def opSMB(self, x, mask):
        address = x()
        self.memory[address] |= mask

    def opSTZ(self, x):
        self.memory[x()] = 0x00

    def opTSB(self, x):
        address = x()
        m = self.memory[address]
        self.p &= ~self.ZERO
        z = m & self.a
        if z == 0:
            self.p |= self.ZERO
        self.memory[address] = m | self.a

    def opTRB(self, x):
        address = x()
        m = self.memory[address]
        self.p &= ~self.ZERO
        z = m & self.a
        if z == 0:
            self.p |= self.ZERO
        self.memory[address] = m & ~self.a

    def opADC(self, x):
        return self._opADC(x, flags_use_adjusted_result=True)

    def _opSBCDecimal(self, x):
        """SBC opcode in binary mode (non-BCD)"""

        data = self.ByteAt(x())

        decimalcarry = 0
        #adjust0 = 0
        #adjust1 = 0

        #nibble0 = (self.a & 0xf) + (~data & 0xf) + (self.p & self.CARRY)
        #if nibble0 <= 0xf:
            #halfcarry = 0
            #adjust0 = 10 # 0xa = -0x6
        #nibble1 = ((self.a >> 4) & 0xf) + ((~data >> 4) & 0xf) + halfcarry
        #if nibble1 <= 0xf:
            #adjust1 = 10 << 4 # -0x60

        # the ALU outputs are not decimally adjusted
        aluresult = self.a + (~data & self.byteMask) + \
                    (self.p & self.CARRY)

        if aluresult > self.byteMask:
            decimalcarry = 1
        aluresult &= self.byteMask

        #A2 = (self.a + ~data + (self.p & self.CARRY))
        #print "A = %02X, %02X, A2 = %02X, a=%02X, data=%02X, alu=%02X" % (A, (A & self.byteMask), A2, self.a, data, aluresult)
        #assert A == A2

        # but the final result will be adjusted
        #nibble0 = (aluresult + adjust0) & 0xf
        #nibble1 = ((aluresult + adjust1) >> 4) & 0xf

        # Update result for use in setting flags below
        #adjresult = (nibble1 << 4) + nibble0

        A = self.a - data + (self.p & self.CARRY) - 1
        AL = (self.a & 0xf) - (data & 0xf) + (self.p & self.CARRY) - 1
        assert (A & self.byteMask)  == aluresult

        # XXX
        if A < 0:
            #print A, A2
            #assert adjust1, (A, adjust1)
            A -= 0x60

        if AL < 0:
            #assert adjust0, (AL, adjust0)
            A -= 0x6

        #if (A & self.byteMask) != adjresult:
        #    print "a=%02X data=%02X carry=%02X, res=%02X, adj=%02X" % (
        #        self.a, data, self.p & self.CARRY, A & self.byteMask, adjresult)
            #assert False

        adjresult = A & self.byteMask

        self.p &= ~(self.CARRY | self.ZERO | self.NEGATIVE | self.OVERFLOW)
        if adjresult == 0:
            self.p |= self.ZERO
        else:
            self.p |= adjresult & self.NEGATIVE
        if decimalcarry == 1:
            self.p |= self.CARRY
        if ((self.a ^ data) & (self.a ^ aluresult)) & self.NEGATIVE:
            self.p |= self.OVERFLOW
        self.a = adjresult

    # instructions

    @instruction(name="BRK", mode="imp", cycles=7)
    def inst_0x00(self):
        # pc has already been increased one
        pc = (self.pc + 1) & self.addrMask
        self.stPushWord(pc)

        self.p |= self.BREAK
        self.stPush(self.p | self.BREAK | self.UNUSED)

        self.p |= self.INTERRUPT
        self.pc = self.WordAt(self.IRQ)

        # 65C02 clears decimal flag, NMOS 6502 does not
        self.p &= ~self.DECIMAL

    @instruction(name="TSB", mode="zpg", cycles=5)
    def inst_0x04(self):
        self.opTSB(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="RMB0", mode="zpg", cycles=5)
    def inst_0x07(self):
        self.opRMB(self.ZeroPageAddr, 0xFE)
        self.pc += 1

    @instruction(name="TSB", mode="abs", cycles=6)
    def inst_0x0c(self):
        self.opTSB(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="ORA", mode="zpi", cycles=5)
    def inst_0x12(self):
        self.opORA(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="TRB", mode="zpg", cycles=5)
    def inst_0x14(self):
        self.opTRB(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="RMB1", mode="zpg", cycles=5)
    def inst_0x17(self):
        self.opRMB(self.ZeroPageAddr, 0xFD)
        self.pc += 1

    @instruction(name="INC", mode="acc", cycles=2)
    def inst_0x1a(self):
        self.opINCR(None)

    @instruction(name="TRB", mode="abs", cycles=6)
    def inst_0x1c(self):
        self.opTRB(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="RMB2", mode="zpg", cycles=5)
    def inst_0x27(self):
        self.opRMB(self.ZeroPageAddr, 0xFB)
        self.pc += 1

    @instruction(name="AND", mode="zpi", cycles=5)
    def inst_0x32(self):
        self.opAND(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="BIT", mode="zpx", cycles=4)
    def inst_0x34(self):
        self.opBIT(self.ZeroPageXAddr)
        self.pc += 1

    @instruction(name="RMB3", mode="zpg", cycles=5)
    def inst_0x37(self):
        self.opRMB(self.ZeroPageAddr, 0xF7)
        self.pc += 1

    @instruction(name="DEC", mode="acc", cycles=2)
    def inst_0x3a(self):
        self.opDECR(None)

    @instruction(name="BIT", mode="abx", cycles=4)
    def inst_0x3c(self):
        self.opBIT(self.AbsoluteXAddr)
        self.pc += 2

    @instruction(name="RMB4", mode="zpg", cycles=5)
    def inst_0x47(self):
        self.opRMB(self.ZeroPageAddr, 0xEF)
        self.pc += 1

    @instruction(name="EOR", mode="zpi", cycles=5)
    def inst_0x52(self):
        self.opEOR(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="RMB5", mode="zpg", cycles=5)
    def inst_0x57(self):
        self.opRMB(self.ZeroPageAddr, 0xDF)
        self.pc += 1

    @instruction(name="PHY", mode="imp", cycles=3)
    def inst_0x5a(self):
        self.stPush(self.y)

    @instruction(name="STZ", mode="imp", cycles=3)
    def inst_0x64(self):
        self.opSTZ(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="RMB6", mode="zpg", cycles=5)
    def inst_0x67(self):
        self.opRMB(self.ZeroPageAddr, 0xBF)
        self.pc += 1

    @instruction(name="JMP", mode="ind", cycles=6)
    def inst_0x6c(self):
        ta = self.WordAt(self.pc)
        self.pc = self.WordAt(ta)

    @instruction(name="ADC", mode="zpi", cycles=5)
    def inst_0x72(self):
        self.opADC(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="STZ", mode="zpx", cycles=4)
    def inst_0x74(self):
        self.opSTZ(self.ZeroPageXAddr)
        self.pc += 1

    @instruction(name="RMB7", mode="zpg", cycles=5)
    def inst_0x77(self):
        self.opRMB(self.ZeroPageAddr, 0x7F)
        self.pc += 1

    @instruction(name="PLY", mode="imp", cycles=4)
    def inst_0x7a(self):
        self.y = self.stPop()
        self.FlagsNZ(self.y)

    @instruction(name="JMP", mode="iax", cycles=6)
    def inst_0x7c(self):
        self.pc = self.WordAt(self.IndirectAbsXAddr())

    @instruction(name="BRA", mode="rel", cycles=1, extracycles=1)
    def inst_0x80(self):
        self.BranchRelAddr()

    @instruction(name="SMB0", mode="zpg", cycles=5)
    def inst_0x87(self):
        self.opSMB(self.ZeroPageAddr, 0x01)
        self.pc += 1

    @instruction(name="BIT", mode="imm", cycles=2)
    def inst_0x89(self):
        # This instruction (BIT #$12) does not use opBIT because in the
        # immediate mode, BIT only affects the Z flag.
        tbyte = self.ImmediateByte()
        self.p &= ~(self.ZERO)
        if (self.a & tbyte) == 0:
            self.p |= self.ZERO
        self.pc += 1

    @instruction(name="STA", mode="zpi", cycles=5)
    def inst_0x92(self):
        self.opSTA(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="SMB1", mode="zpg", cycles=5)
    def inst_0x97(self):
        self.opSMB(self.ZeroPageAddr, 0x02)
        self.pc += 1

    @instruction(name="STZ", mode="abs", cycles=4)
    def inst_0x9c(self):
        self.opSTZ(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="STZ", mode="abx", cycles=5)
    def inst_0x9e(self):
        self.opSTZ(self.AbsoluteXAddr)
        self.pc += 2

    @instruction(name="SMB2", mode="zpg", cycles=5)
    def inst_0xa7(self):
        self.opSMB(self.ZeroPageAddr, 0x04)
        self.pc += 1

    @instruction(name="LDA", mode="zpi", cycles=5)
    def inst_0xb2(self):
        self.opLDA(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="SMB3", mode="zpg", cycles=5)
    def inst_0xb7(self):
        self.opSMB(self.ZeroPageAddr, 0x08)
        self.pc += 1

    @instruction(name="SMB4", mode="zpg", cycles=5)
    def inst_0xc7(self):
        self.opSMB(self.ZeroPageAddr, 0x10)
        self.pc += 1

    @instruction(name="WAI", mode='imp', cycles=3)
    def inst_0xcb(self):
        self.waiting = True

    @instruction(name="CMP", mode='zpi', cycles=5)
    def inst_0xd2(self):
        self.opCMPR(self.ZeroPageIndirectAddr, self.a)
        self.pc += 1

    @instruction(name="SMB5", mode="zpg", cycles=5)
    def inst_0xd7(self):
        self.opSMB(self.ZeroPageAddr, 0x20)
        self.pc += 1

    @instruction(name="PHX", mode="imp", cycles=3)
    def inst_0xda(self):
        self.stPush(self.x)

    @instruction(name="SMB6", mode="zpg", cycles=5)
    def inst_0xe7(self):
        self.opSMB(self.ZeroPageAddr, 0x40)
        self.pc += 1

    @instruction(name="SBC", mode="zpi", cycles=5)
    def inst_0xf2(self):
        self.opSBC(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="SMB7", mode="zpg", cycles=5)
    def inst_0xf7(self):
        self.opSMB(self.ZeroPageAddr, 0x80)
        self.pc += 1

    @instruction(name="PLX", mode="imp", cycles=4)
    def inst_0xfa(self):
        self.x = self.stPop()
        self.FlagsNZ(self.x)
