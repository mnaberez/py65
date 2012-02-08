from py65.devices import mpu6502
from py65.utils.devices import make_instruction_decorator

class MPU(mpu6502.MPU):
    def __init__(self, *args, **kwargs):
        mpu6502.MPU.__init__(self, *args, **kwargs)
        self.name = '65C02'
        self.waiting = False

    def step(self):
        if self.waiting:
            self.processorCycles += 1
        else:
            mpu6502.MPU.step(self)
        return self

    # Make copies of the lists
    instruct    = mpu6502.MPU.instruct[:]
    cycletime   = mpu6502.MPU.cycletime[:]
    extracycles = mpu6502.MPU.extracycles[:]
    disassemble = mpu6502.MPU.disassemble[:]

    instruction = make_instruction_decorator(instruct, disassemble,
                                                cycletime, extracycles)

    # addressing modes

    def ZeroPageIndirectAddr(self):
        return self.WordAt( 255 & (self.ByteAt(self.pc)))

    def AccumulatorAddr(self):
        return self.a

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
        if z != 0:
            self.p |= self.ZERO
        self.memory[address] = m | self.a

    def opTRB(self, x):
        address = x()
        m = self.memory[address]
        self.p &= ~self.ZERO
        z = m & self.a
        if z != 0:
            self.p |= self.ZERO
        self.memory[address] = m & ~self.a

    # instructions

    @instruction(name="RMB0", mode="zpg", cycles=5)
    def inst_0x07(self):
        self.opRMB(self.ZeroPageAddr, 0xFE)
        self.pc += 1

    @instruction(name="ORA", mode="zpi", cycles=5)
    def inst_0x12(self):
        self.opORA(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="RMB1", mode="zpg", cycles=5)
    def inst_0x17(self):
        self.opRMB(self.ZeroPageAddr, 0xFD)
        self.pc += 1

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

    @instruction(name="ADC", mode="zpi", cycles=5)
    def inst_0x72(self):
        self.opADC(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="STZ", mode="zpx", cycles=4)
    def inst_0x74(self):
        self.opSTZ(self.ZeroPageXAddr)
        self.pc += 1

    @instruction(name="PLY", mode="imp", cycles=4)
    def inst_0x7a(self):
        self.y = self.stPop()
        self.FlagsNZ(self.y)

    @instruction(name="RMB7", mode="zpg", cycles=5)
    def inst_0x77(self):
        self.opRMB(self.ZeroPageAddr, 0x7F)
        self.pc += 1

    @instruction(name="SMB0", mode="zpg", cycles=5)
    def inst_0x87(self):
        self.opSMB(self.ZeroPageAddr, 0x01)
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

    @instruction(name="SMB7", mode="zpg", cycles=5)
    def inst_0xf7(self):
        self.opSMB(self.ZeroPageAddr, 0x80)
        self.pc += 1

    @instruction(name="PLX", mode="imp", cycles=4)
    def inst_0xfa(self):
        self.x = self.stPop()
        self.FlagsNZ(self.x)

    @instruction(name="TSB", mode="zpg", cycles=5)
    def inst_0x04(self):
        self.opTSB(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="TSB", mode="abs", cycles=6)
    def inst_0x0c(self):
        self.opTSB(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="TRB", mode="zpg", cycles=5)
    def inst_0x14(self):
        self.opTRB(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="INC", mode="acc", cycles=2)
    def inst_0x1a(self):
        self.opINCR(None)

    @instruction(name="TRB", mode="abs", cycles=6)
    def inst_0x1c(self):
        self.opTRB(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="DEC", mode="acc", cycles=2)
    def inst_0x3a(self):
        self.opDECR(None)

    @instruction(name="BRA", mode="rel", cycles=1, extracycles=1)
    def inst_0x80(self):
        self.BranchRelAddr()

    @instruction(name="WAI", mode='imp', cycles=3)
    def inst_0xCB(self):
        self.waiting = True

    @instruction(name="CMP", mode='zpi', cycles=5)
    def inst_0xD2(self):
        self.opCPY(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="SBC", mode="zpi", cycles=5)
    def inst_0xf2(self):
        self.opSBC(self.ZeroPageIndirectAddr)
        self.pc += 1

