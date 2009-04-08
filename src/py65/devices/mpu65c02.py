from py65.devices.mpu6502 import MPU as NMOS6502
from py65.utils.devices import make_instruction_decorator

class MPU(NMOS6502):
    def __init__(self, *args, **kwargs):
        NMOS6502.__init__(self, *args, **kwargs)
        self.name = '65C02'

    instruct    = NMOS6502.instruct[:]
    cycletime   = NMOS6502.cycletime[:]
    extracycles = NMOS6502.extracycles[:]

    instruction = \
      make_instruction_decorator(instruct, cycletime, extracycles)


    # operations

    def opSTZ(self, x):
        self.memory[x()] = 0x00


    # instructions

    @instruction(0x64, 3)
    def i64(self):
        self.opSTZ(self.ZeroPageAddr)
        self.pc += 1

    @instruction(0x74, 4)
    def i74(self):
        self.opSTZ(self.ZeroPageXAddr)
        self.pc += 1

    @instruction(0x9c, 4)
    def i9c(self):
        self.opSTZ(self.AbsoluteAddr)
        self.pc += 2

    @instruction(0x9e, 5)
    def i9e(self):
        self.opSTZ(self.AbsoluteXAddr)
        self.pc+=2

