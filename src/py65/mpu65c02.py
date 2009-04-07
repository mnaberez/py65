#from py65.utils.conversions import convert_to_bin, convert_to_bcd
import mpu6502 

class MPU(mpu6502.MPU):
  def __init__(self, memory=None, pc=0x0000, debug=False):
    mpu6502.MPU.__init__(self, memory=memory, pc=pc, debug=debug)
    self.name = '65C02'

  def opSTZ(self, x):
      self.memory[x()] = 0x00

  def i64(self):
      self.opSTZ(self.ZeroPageAddr)
      self.pc += 1

  # code pages

  instruct = mpu6502.MPU.instruct[:]
  instruct[0x64] = i64

  cycletime = mpu6502.MPU.cycletime[:]
  cycletime[0x64] = 3

  extracycles = mpu6502.MPU.extracycles[:]
  extracycles[0x64] = 0

