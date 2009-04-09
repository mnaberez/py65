from py65.devices.mpu6502 import MPU as NMOS6502
from py65.utils.devices import make_instruction_decorator

class MPU(NMOS6502):
    def __init__(self, *args, **kwargs):
        NMOS6502.__init__(self, *args, **kwargs)
        self.name = '65C02'

    instruct    = NMOS6502.instruct[:]
    cycletime   = NMOS6502.cycletime[:]
    extracycles = NMOS6502.extracycles[:]
    disassemble = NMOS6502.disassemble[:]

    instruction = make_instruction_decorator(instruct, disassemble, 
                                                cycletime, extracycles)

    # addressing modes

    def ZeroPageIndirectAddr(self):
        return self.WordAt( 255 & (self.ByteAt(self.pc)))

    # operations

    def opSTZ(self, x):
        self.memory[x()] = 0x00

    def opTSB(self, x):
        address = x()
        m = self.memory[address] 
        self.flags &= ~self.ZERO
        z = m & self.a
        if z != 0:
            self.flags |= self.ZERO
        self.memory[address] = m | self.a

    def opTRB(self, x):
        address = x()
        m = self.memory[address] 
        self.flags &= ~self.ZERO
        z = m & self.a
        if z != 0:
            self.flags |= self.ZERO
        self.memory[address] = m & ~self.a

    # instructions
    
    @instruction(name="ORA", mode="zpi", cycles=5)
    def i12(self):
        self.opORA(self.IndirectXAddr)
        self.pc += 1

    @instruction(name="AND", mode="zpi", cycles=5)
    def i32(self):
        self.opAND(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="EOR", mode="zpi", cycles=5)
    def i52(self):
        self.opEOR(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="PHY", mode="imp", cycles=3)
    def i5a(self):
        self.stPush(self.y)

    @instruction(name="STZ", mode="imp", cycles=3)
    def i64(self):
        self.opSTZ(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="ADC", mode="zpi", cycles=5)
    def i72(self):
        self.opADC(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="STZ", mode="zpx", cycles=4)
    def i74(self):
        self.opSTZ(self.ZeroPageXAddr)
        self.pc += 1

    @instruction(name="PHY", mode="imp", cycles=4)
    def i7a(self):
        self.y = self.stPop()
        self.FlagsNZ(self.y)    

    @instruction(name="STA", mode="zpi", cycles=5)
    def i92(self):
        self.opSTA(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="STZ", mode="abs", cycles=4)
    def i9c(self):
        self.opSTZ(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="STZ", mode="abx", cycles=5)
    def i9e(self):
        self.opSTZ(self.AbsoluteXAddr)
        self.pc += 2

    @instruction(name="LDA", mode="zpi", cycles=5)
    def ib2(self):
        self.opLDA(self.ZeroPageIndirectAddr)
        self.pc += 1

    @instruction(name="PHX", mode="imp", cycles=3)
    def ida(self):
        self.stPush(self.x)

    @instruction(name="PLX", mode="imp", cycles=4)
    def ifa(self):
        self.x = self.stPop()
        self.FlagsNZ(self.x)

    @instruction(name="TSB", mode="zpg", cycles=5)
    def i04(self):
        self.opTSB(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="TSB", mode="abs", cycles=6)
    def i0c(self):
        self.opTSB(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="TSB", mode="zpg", cycles=5)
    def i04(self):
        self.opTSB(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="TSB", mode="abs", cycles=6)
    def i0c(self):
        self.opTSB(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="TRB", mode="zpg", cycles=5)
    def i14(self):
        self.opTRB(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="TRB", mode="abs", cycles=6)
    def i1c(self):
        self.opTRB(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="SBC", mode="zpi", cycles=5)
    def if2(self):
        self.opSBC(self.ZeroPageIndirectAddr)
        self.pc += 1

