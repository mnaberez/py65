#from py65.utils.conversions import convert_to_bin, convert_to_bcd
import mpu6502 

def make_instruction_decorator(instruct, cycletime, extracycles):
    def instruction(opcode, opcycles, opextracycles=0):
        def decorate(f):
            instruct[opcode] = f
            cycletime[opcode] = opcycles
            extracycles[opcode] = opextracycles
            return f # Return the original function
        return decorate
    return instruction


class MPU(mpu6502.MPU):
  def __init__(self, memory=None, pc=0x0000, debug=False):
    mpu6502.MPU.__init__(self, memory=memory, pc=pc, debug=debug)
    self.name = '65C02'

  instruct = mpu6502.MPU.instruct[:]
  cycletime = mpu6502.MPU.cycletime[:]
  extracycles = mpu6502.MPU.extracycles[:]

  instruction = \
      make_instruction_decorator(instruct, cycletime, extracycles)

  def opSTZ(self, x):
      self.memory[x()] = 0x00

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

