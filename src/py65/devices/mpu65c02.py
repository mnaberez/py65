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

    # operations

    def opSTZ(self, x):
        self.memory[x()] = 0x00


    # instructions

    @instruction(name="PHY", mode="imp", cycles=3)
    def i5a(self):
        self.stPush(self.y)

    @instruction(name="STZ", mode="imp", cycles=3)
    def i64(self):
        self.opSTZ(self.ZeroPageAddr)
        self.pc += 1

    @instruction(name="STZ", mode="zpx", cycles=4)
    def i74(self):
        self.opSTZ(self.ZeroPageXAddr)
        self.pc += 1

    @instruction(name="PHY", mode="imp", cycles=4)
    def i7a(self):
      self.y = self.stPop()
      self.FlagsNZ(self.y)    

    @instruction(name="STZ", mode="abs", cycles=4)
    def i9c(self):
        self.opSTZ(self.AbsoluteAddr)
        self.pc += 2

    @instruction(name="STZ", mode="abx", cycles=5)
    def i9e(self):
        self.opSTZ(self.AbsoluteXAddr)
        self.pc+=2

    @instruction(name="PHX", mode="imp", cycles=3)
    def ida(self):
        self.stPush(self.x)

    @instruction(name="PLX", mode="imp", cycles=4)
    def ifa(self):
      self.x = self.stPop()
      self.FlagsNZ(self.x)

     