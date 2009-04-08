from py65.utils.conversions import convert_to_bin, convert_to_bcd
from py65.utils.devices import make_instruction_decorator

class MPU:
  # vectors
  ResetTo = 0xfffc
  IrqTo   = 0xfffe
  NMITo   = 0xfffa

  # processor flags
  NEGATIVE  = 128
  OVERFLOW  = 64
  UNUSED    = 32
  BREAK     = 16
  DECIMAL   = 8
  INTERRUPT = 4
  ZERO      = 2
  CARRY     = 1

  def __init__(self, memory=None, pc=0x0000, debug=False):
    # config
    self.debug = debug
    self.name = '6502'
    
    # vm status
    self.breakFlag = False
    self.excycles = 0
    self.addcycles = False
    self.processorCycles = 0
    self.internalCycleDelay = 0

    if memory is None:
        memory = 0x10000 * [0x00]
    self.memory = memory
    self.start_pc = pc

    # init
    self.reset()

  def __repr__(self):
    out = '<%s: A=%02x, X=%02x, Y=%02x, Flags=%02x, SP=%02x, PC=%04x>'
    return out % (self.name, self.a, self.x, self.y,
                  self.flags, self.sp, self.pc)

  def step(self):
    breakFlag = False
    instructCode = self.ImmediateByte()
    self.pc +=1
    self.pc &=0xffff
    self.excycles = 0
    self.addcycles = self.extracycles[instructCode]
    self.instruct[instructCode](self)
    self.processorCycles += self.cycletime[instructCode]+self.excycles
    self.pc &= 0xffff
    return self

  def reset(self):
    self.pc = self.start_pc
    self.sp = 255
    self.a = 0
    self.x = 0
    self.y = 0
    self.flags = self.UNUSED
    self.breakFlag = False
    self.processorCycles = 0

  # Helpers for addressing modes

  def ByteAt(self, addr):
    return self.memory[addr]

  def WordAt(self, addr):
    return self.ByteAt(addr) + (self.ByteAt(addr + 1) << 8)
  
  # Addressing modes

  def ImmediateByte(self):
    return self.ByteAt(self.pc)

  def ZeroPageAddr(self):
    return self.ByteAt(self.pc)

  def ZeroPageXAddr(self):
    return 255 & (self.x + self.ByteAt(self.pc))

  def ZeroPageYAddr(self):
    return 255 & (self.y + self.ByteAt(self.pc))

  def IndirectXAddr(self):
    return self.WordAt( 255 & (self.ByteAt(self.pc) + self.x))

  def IndirectYAddr(self):
    if self.addcycles:
      a1 = self.WordAt(self.ByteAt(self.pc))
      a2 = (a1+self.y) & 0xffff
      if (a1 & 0xff00) != (a2 & 0xff00):
        self.excycles += 1
      return a2
    else:
      return (self.WordAt(self.ByteAt(self.pc))+self.y)&0xffff

  def AbsoluteAddr(self):
    return self.WordAt(self.pc)

  def AbsoluteXAddr(self):
    if self.addcycles:
      a1 = self.WordAt(self.pc)
      a2 = (a1 + self.x) & 0xffff
      if (a1 & 0xff00) != (a2 & 0xff00):
        self.excycles += 1
      return a2
    else:
      return (self.WordAt(self.pc)+self.x)&0xffff

  def AbsoluteYAddr(self):
    if self.addcycles:
      a1 = self.WordAt(self.pc)
      a2 = (a1 + self.y) & 0xffff
      if (a1 & 0xff00) != (a2 & 0xff00):
        self.excycles += 1
      return a2
    else:
      return (self.WordAt(self.pc)+self.y)&0xffff

  def BranchRelAddr(self):
    self.excycles += 1
    addr = self.ImmediateByte()
    self.pc += 1

    if addr & 128:
      addr = self.pc - (addr ^ 0xFF) - 1
    else:
      addr = self.pc + addr

    if (self.pc & 0xff00) != (addr & 0xff00):
      self.excycles += 1

    self.pc = addr & 0xffff

  # stack

  def stPush(self,z):
    self.memory[self.sp+256] = z&255
    self.sp -= 1
    self.sp &= 255

  def stPop(self):
    self.sp += 1
    self.sp &= 255
    return self.ByteAt(self.sp+256)

  def stPushWord(self, z):
    self.stPush((z>>8)&255)
    self.stPush(z&255)
  
  def stPopWord(self):
    z = self.stPop()
    z += 256*self.stPop()
    return z

  def FlagsNZ(self, value):
    self.flags &= ~(self.ZERO + self.NEGATIVE)
    if value == 0:
      self.flags |= self.ZERO
    else:
      self.flags |= value & self.NEGATIVE

  # operations

  def opORA(self, x):
    self.a |= self.ByteAt(x())
    self.FlagsNZ(self.a)

  def opASL(self, x):
    addr = x()
    tbyte = self.ByteAt(addr)
    self.flags &= ~(self.CARRY + self.NEGATIVE + self.ZERO)

    if tbyte & 128:
      self.flags |= self.CARRY
      
    tbyte = (tbyte << 1) & 0xFF
    if tbyte:
      self.flags |= tbyte & 128
    else:
      self.flags |= self.ZERO

    self.memory[addr] = tbyte

  def opLSR(self, x):
    addr = x()
    tbyte = self.ByteAt(addr)
    self.flags &=~(self.CARRY+self.NEGATIVE+self.ZERO)
    self.flags |=tbyte&1

    tbyte = tbyte >> 1
    if tbyte:
      pass # {}
    else:
      self.flags |= self.ZERO
    self.memory[addr]=tbyte

  def opBCL(self, x):
    if self.flags & x: 
      self.pc += 1
    else:
      self.BranchRelAddr()

  def opBST(self, x):
    if self.flags & x:
      self.BranchRelAddr()
    else:
      self.pc+=1

  def opCLR(self, x):
    self.flags &=~x

  def opSET(self, x):
    self.flags |= x

  def opAND(self, x):
    self.a &= self.ByteAt(x())
    self.FlagsNZ(self.a)

  def opBIT(self, x):
    tbyte = self.ByteAt(x())
    self.flags &=~(self.ZERO+self.NEGATIVE+self.OVERFLOW)
    if (self.a & tbyte) == 0:
      self.flags |= self.ZERO
    self.flags |= tbyte&(128+64)

  def opROL(self, x):
    addr = x()
    tbyte = self.ByteAt(addr)
    if self.flags & self.CARRY:
      if tbyte & 128:
        pass
      else:
        self.flags &= ~self.CARRY
      tbyte = (tbyte << 1) | 1
    else:
      if tbyte & 128:
        self.flags |= self.CARRY
      tbyte = tbyte << 1
    self.FlagsNZ(tbyte)
    self.memory[addr] = tbyte & 0xFF

  def opEOR(self, x):
    self.a ^= self.ByteAt(x())
    self.FlagsNZ(self.a)

  def opADC(self, x):
    data=self.ByteAt(x())
    if self.flags & self.DECIMAL:
      if self.flags & self.CARRY:
        tmp = 1
      else:
        tmp = 0
      data = convert_to_bin(data) + convert_to_bin(self.a) + tmp
      self.flags &= ~(self.CARRY+self.OVERFLOW+self.NEGATIVE+self.ZERO)
      if data > 99:
        self.flags |= self.CARRY + self.OVERFLOW
        data -= 100

      if data == 0:
        self.flags |= self.ZERO
      else:
        self.flags |= data & 128
      self.a = convert_to_bcd(data)
    else:
      if self.flags & self.CARRY:
        tmp = 1
      else:
        tmp = 0
      data += self.a + tmp
      self.flags &= ~(self.CARRY+self.OVERFLOW+self.NEGATIVE+self.ZERO)
      if data > 255:
        self.flags|=self.OVERFLOW+self.CARRY
        data &=255
      if data == 0:
        self.flags |= self.ZERO
      else:
        self.flags |= data & 128
      self.a = data

  def opROR(self, x):
    addr=x()
    tbyte = self.ByteAt(addr)
    if self.flags & self.CARRY:
      if tbyte & 1:
        pass # {}
      else:
        self.flags &=~ self.CARRY
      tbyte=(tbyte>>1)|128
    else:
      if tbyte & 1:
        self.flags |= self.CARRY
      tbyte=tbyte>>1
    self.FlagsNZ(tbyte)
    self.memory[addr]=tbyte

  def opSTA(self, x):
    self.memory[x()] = self.a

  def opSTY(self, x):
    self.memory[x()] = self.y

  def opSTX(self, y):
    self.memory[y()] = self.x

  def opCPY(self, x):
    tbyte=self.ByteAt(x())
    self.flags &=~(self.CARRY+self.ZERO+self.NEGATIVE)
    if self.y == tbyte:
      self.flags |= self.CARRY + self.ZERO
    elif self.y > tbyte:
       self.flags |= self.CARRY
    else:
      self.flags |= self.NEGATIVE

  def opCPX(self, y):
    tbyte = self.ByteAt(y())
    self.flags &=~(self.CARRY+self.ZERO+self.NEGATIVE)
    if self.x == tbyte:
      self.flags |= self.CARRY + self.ZERO
    elif self.x > tbyte:
      self.flags |= self.CARRY
    else:
      self.flags |= self.NEGATIVE

  def opCMP(self, x):
    tbyte = self.ByteAt(x())
    self.flags &= ~(self.CARRY+self.ZERO+self.NEGATIVE)
    if self.a == tbyte:
      self.flags |= self.CARRY + self.ZERO
    elif self.a > tbyte:
      self.flags |= self.CARRY
    else:
      self.flags |= self.NEGATIVE

  def opSBC(self, x):
    data = self.ByteAt(x())
    if self.flags & self.DECIMAL:
      if self.flags & self.CARRY:
        borrow = 0
      else:
        borrow = 1
    
      data = convert_to_bin(self.a) - convert_to_bin(data) - borrow
      self.flags &= ~(self.CARRY + self.ZERO + self.NEGATIVE + self.OVERFLOW)
      if data == 0:
        self.flags |= self.ZERO + self.CARRY
      elif data > 0:
        self.flags |= self.CARRY
      else:
        self.flags |= self.NEGATIVE
        data +=100
      self.a = convert_to_bcd(data)
    else:
      if self.flags & self.CARRY:
        borrow = 0
      else:
        borrow = 1

      data = self.a - data - borrow
      self.flags &= ~(self.CARRY + self.ZERO + self.OVERFLOW + self.NEGATIVE)
      if data == 0:
        self.flags |= self.ZERO + self.CARRY
      elif data > 0:
        self.flags |= self.CARRY
      else:
        self.flags |= self.OVERFLOW
      self.flags |= data & self.NEGATIVE
      self.a = data & 0xFF

  def opDECR(self, x):
    addr = x()
    tbyte = self.ByteAt(addr)
    self.flags &= ~(self.ZERO + self.NEGATIVE)
    tbyte = (tbyte - 1) & 0xFF
    if tbyte:
      self.flags |= tbyte & self.NEGATIVE
    else:
      self.flags |= self.ZERO
    self.memory[addr] = tbyte

  def opINCR(self, x):
    addr = x()
    tbyte = self.ByteAt(addr)
    self.flags &= ~(self.ZERO + self.NEGATIVE)
    tbyte = (tbyte + 1) & 0xFF
    if tbyte:
      self.flags |= tbyte & self.NEGATIVE
    else:
      self.flags |= self.ZERO
    self.memory[addr] = tbyte

  def opLDA(self, x):
    self.a = self.ByteAt(x())
    self.FlagsNZ(self.a)

  def opLDY(self, x):
    self.y = self.ByteAt(x())
    self.FlagsNZ(self.y)

  def opLDX(self, y):
    self.x = self.ByteAt(y())
    self.FlagsNZ(self.x)

  # instructions

  def ini(self):
    if self.debug:
      raise NotImplementedError
    self.pc += 1

  instruct    = [ini] * 256
  cycletime   = [0] * 256
  extracycles = [0] * 256

  instruction = \
    make_instruction_decorator(instruct, cycletime, extracycles)

  @instruction(0x0, 7, 0)
  def i00(self):
    pc = (self.pc + 2) & 0xFFFF
    self.stPushWord(pc)

    self.flags |= self.BREAK
    self.stPush(self.flags)

    self.flags |= self.INTERRUPT
    self.pc = self.WordAt(self.IrqTo)

    self.breakFlag = True

  @instruction(0x1, 6, 0)
  def i01(self):
    self.opORA(self.IndirectXAddr)
    self.pc += 1

  @instruction(0x5, 3, 0)
  def i05(self):
    self.opORA(self.ZeroPageAddr)
    self.pc += 1

  @instruction(0x6, 5, 0)
  def i06(self):
    self.opASL(self.ZeroPageAddr)
    self.pc += 1
  
  @instruction(0x8, 3, 0)
  def i08(self):
    self.stPush(self.flags)
  
  @instruction(0x9, 2, 0)
  def i09(self):
    self.a |= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1
  
  @instruction(0xa, 2, 0)
  def i0a(self):
    if self.a & 128:
      self.flags |= self.CARRY
    else:
      self.flags &= ~self.CARRY
    self.a = self.a << 1
    self.FlagsNZ(self.a)
    self.a &= 255

  @instruction(0xd, 4, 0)
  def i0d(self):
    self.opORA(self.AbsoluteAddr)
    self.pc += 2
  
  @instruction(0xe, 6, 0)
  def i0e(self):
    self.opASL(self.AbsoluteAddr)
    self.pc += 2
  
  @instruction(0x10, 2, 2)
  def i10(self):
    self.opBCL(self.NEGATIVE)
  
  @instruction(0x11, 5, 1)
  def i11(self):
    self.opORA(self.IndirectYAddr)
    self.pc += 1
  
  @instruction(0x15, 4, 0)
  def i15(self):
    self.opORA(self.ZeroPageXAddr)
    self.pc += 1
  
  @instruction(0x16, 6, 0)
  def i16(self):
    self.opASL(self.ZeroPageXAddr)
    self.pc += 1
  
  @instruction(0x18, 2, 0)
  def i18(self):
    self.opCLR(self.CARRY)
  
  @instruction(0x19, 4, 1)
  def i19(self):
    self.opORA(self.AbsoluteYAddr)
    self.pc += 2 
  
  @instruction(0x1d, 4, 1)
  def i1d(self):
    self.opORA(self.AbsoluteXAddr)
    self.pc += 2

  @instruction(0x1e, 7, 0)
  def i1e(self):
    self.opASL(self.AbsoluteXAddr)
    self.pc += 2

  @instruction(0x20, 6, 0)
  def i20(self): 
    self.stPushWord((self.pc+1)&0xffff)
    self.pc=self.WordAt(self.pc)
  
  @instruction(0x21, 6, 0)
  def i21(self):
    self.opAND(self.IndirectXAddr)
    self.pc += 1
  
  @instruction(0x24, 3, 0)
  def i24(self):
    self.opBIT(self.ZeroPageAddr)
    self.pc += 1
  
  @instruction(0x25, 3, 0)
  def i25(self):
    self.opAND(self.ZeroPageAddr)
    self.pc += 1
  
  @instruction(0x26, 5, 0)
  def i26(self):
    self.opROL(self.ZeroPageAddr)
    self.pc += 1

  @instruction(0x28, 4, 0)
  def i28(self):
    self.flags = self.stPop()
  
  @instruction(0x29, 2, 0)
  def i29(self):
    self.a &= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1

  @instruction(0x2a, 2, 0)
  def i2a(self):
    if self.flags & self.CARRY:
      if (self.a & 128) == 0:
        self.flags &=~self.CARRY
      self.a = (self.a<<1) | 1
    else:
      if self.a & 128:
        self.flags |= self.CARRY
      self.a = self.a << 1
    self.FlagsNZ(self.a)
    self.a &= 255

  @instruction(0x2c, 4, 0)
  def i2c(self):
    self.opBIT(self.AbsoluteAddr)
    self.pc+=2

  @instruction(0x2d, 4, 0)
  def i2d(self):
    self.opAND(self.AbsoluteAddr)
    self.pc+=2

  @instruction(0x2e, 6, 0)
  def i2e(self):
    self.opROL(self.AbsoluteAddr)
    self.pc += 2

  @instruction(0x30, 2, 2)
  def i30(self):
    self.opBST(self.NEGATIVE)

  @instruction(0x31, 5, 1)
  def i31(self):
    self.opAND(self.IndirectYAddr)
    self.pc += 1

  @instruction(0x35, 4, 0)
  def i35(self):
    self.opAND(self.ZeroPageXAddr)
    self.pc += 1

  @instruction(0x36, 6, 0)
  def i36(self):
    self.opROL(self.ZeroPageXAddr)
    self.pc += 1

  @instruction(0x38, 2, 0)
  def i38(self):
    self.opSET(self.CARRY)

  @instruction(0x39, 4, 1)
  def i39(self):
    self.opAND(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(0x3d, 4, 1)
  def i3d(self):
    self.opAND(self.AbsoluteXAddr)
    self.pc += 2 

  @instruction(0x3e, 7, 0)
  def i3e(self):
    self.opROL(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0x40, 6, 0)
  def i40(self):
    self.flags = self.stPop()
    self.pc = self.stPopWord()

  @instruction(0x41, 6, 0)
  def i41(self):
    self.opEOR(self.IndirectXAddr)
    self.pc+=1

  @instruction(0x45, 3, 0)
  def i45(self):
    self.opEOR(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0x46, 5, 0)
  def i46(self):
    self.opLSR(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0x48, 3, 0)
  def i48(self):
    self.stPush(self.a)

  @instruction(0x49, 2, 0)
  def i49(self):
    self.a ^= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc+=1

  @instruction(0x4a, 2, 0)
  def i4a(self):
    self.flags &= ~(self.CARRY+self.NEGATIVE+self.ZERO)
    if self.a & 1:
      self.flags |= self.CARRY

    self.a = self.a >> 1
    if self.a:
      pass # {}
    else:
      self.flags |= self.ZERO
    self.a &= 255

  @instruction(0x4c, 3, 0)
  def i4c(self):
    self.pc=self.WordAt(self.pc)

  @instruction(0x4d, 4, 0)
  def i4d(self):
    self.opEOR(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(0x4e, 6, 0)
  def i4e(self):
    self.opLSR(self.AbsoluteAddr)
    self.pc += 2

  @instruction(0x50, 2, 2)
  def i50(self):
    self.opBCL(self.OVERFLOW)

  @instruction(0x51, 5, 1)
  def i51(self):
    self.opEOR(self.IndirectYAddr)
    self.pc+=1

  @instruction(0x55, 4, 0)
  def i55(self):
    self.opEOR(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(0x56, 6, 0)
  def i56(self):
    self.opLSR(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(0x58, 2, 0)
  def i58(self):
    self.opCLR(self.INTERRUPT)

  @instruction(0x59, 4, 1)
  def i59(self):
    self.opEOR(self.AbsoluteYAddr)
    self.pc +=2

  @instruction(0x5d, 4, 1)
  def i5d(self):
    self.opEOR(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0x5e, 7, 0)
  def i5e(self):
    self.opLSR(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0x60, 6, 0)
  def i60(self):
    self.pc=self.stPopWord()
    self.pc+=1

  @instruction(0x61, 6, 0)
  def i61(self):
    self.opADC(self.IndirectXAddr)
    self.pc+=1

  @instruction(0x65, 3, 0)
  def i65(self):
    self.opADC(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0x66, 5, 0)
  def i66(self):
    self.opROR(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0x68, 4, 0)
  def i68(self):
    self.a = self.stPop()
    self.FlagsNZ(self.a)

  @instruction(0x69, 2, 0)
  def i69(self):
    data = self.ImmediateByte()

    if self.flags & self.CARRY:
      tmp = 1
    else:
      tmp = 0

    if self.flags & self.DECIMAL:
      data = convert_to_bin(data) + convert_to_bin(self.a) + tmp
      self.flags &= ~(self.CARRY+self.OVERFLOW+self.NEGATIVE+self.ZERO)
      if data > 99:
        self.flags |= self.CARRY+self.OVERFLOW
        data -= 100
      if data == 0:
        self.flags |= self.ZERO
      else:
        self.flags |= self.data & 128
      self.a = convert_to_bcd(data)
    else:
      if self.flags & self.CARRY:
        tmp = 1
      else:
        tmp = 0
      data += self.a + tmp
      self.flags &= ~(self.CARRY+self.OVERFLOW+self.NEGATIVE+self.ZERO)
      if data > 255:
        self.flags |= self.OVERFLOW + self.CARRY
        data &= 255
      if data == 0:
        self.flags |= self.ZERO
      else:
        self.flags |= data & 128
      self.a=data
    self.pc += 1

  @instruction(0x6a, 2, 0)
  def i6a(self):
    if self.flags & self.CARRY:
      if (self.a & 1) == 0:
        self.flags &= ~self.CARRY
      self.a = (self.a >> 1) | 128
    else:
      if self.a & 1:
        self.flags |= self.CARRY
      self.a = self.a >> 1
    self.FlagsNZ(self.a)
    self.a &= 255

  @instruction(0x6c, 5, 0)
  def i6c(self):
    ta = self.WordAt(self.pc)
    self.pc = self.WordAt(ta)

  @instruction(0x6d, 4, 0)
  def i6d(self):
    self.opADC(self.AbsoluteAddr)
    self.pc +=2 

  @instruction(0x6e, 6, 0)
  def i6e(self):
    self.opROR(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(0x70, 2, 2)
  def i70(self):
    self.opBST(self.OVERFLOW)

  @instruction(0x71, 5, 1)
  def i71(self):
    self.opADC(self.IndirectYAddr)
    self.pc+=1

  @instruction(0x75, 4, 0)
  def i75(self):
    self.opADC(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(0x76, 6, 0)
  def i76(self):
    self.opROR(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(0x78, 2, 0)
  def i78(self):
    self.opSET(self.INTERRUPT)

  @instruction(0x79, 4, 1)
  def i79(self):
    self.opADC(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(0x7d, 4, 1)
  def i7d(self):
    self.opADC(self.AbsoluteXAddr)
    self.pc+=2
  
  @instruction(0x7e, 7, 0)
  def i7e(self):
    self.opROR(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0x81, 6, 0)
  def i81(self):
    self.opSTA(self.IndirectXAddr)
    self.pc+=1

  @instruction(0x84, 3, 0)
  def i84(self):
    self.opSTY(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0x85, 3, 0)
  def i85(self):
    self.opSTA(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0x86, 3, 0)
  def i86(self):
    self.opSTX(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0x88, 2, 0)
  def i88(self):
    self.y -= 1
    self.y&=255
    self.FlagsNZ(self.y)
  
  @instruction(0x8a, 2, 0)
  def i8a(self):
    self.a=self.x
    self.FlagsNZ(self.a)
  
  @instruction(0x8c, 4, 0)
  def i8c(self):
    self.opSTY(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(0x8d, 4, 0)
  def i8d(self):
    self.opSTA(self.AbsoluteAddr)
    self.pc+=2

  @instruction(0x8e, 4, 0)
  def i8e(self):
    self.opSTX(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(0x90, 2, 2)
  def i90(self):
    self.opBCL(self.CARRY)
  
  @instruction(0x91, 6, 0)
  def i91(self):
    self.opSTA(self.IndirectYAddr)
    self.pc+=1
  
  @instruction(0x94, 4, 0)
  def i94(self):
    self.opSTY(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(0x95, 4, 0)
  def i95(self):
    self.opSTA(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(0x96, 4, 0)
  def i96(self):
    self.opSTX(self.ZeroPageYAddr)
    self.pc+=1
  
  @instruction(0x98, 2, 0)
  def i98(self):
    self.a = self.y
    self.FlagsNZ(self.a)
  
  @instruction(0x99, 5, 0)
  def i99(self):
    self.opSTA(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(0x9a, 2, 0)
  def i9a(self):
    self.sp=self.x

  @instruction(0x9d, 5, 0)
  def i9d(self):
    self.opSTA(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0xa0, 2, 0)
  def ia0(self):
    self.y=self.ImmediateByte()
    self.FlagsNZ(self.y)
    self.pc+=1

  @instruction(0xa1, 6, 0)
  def ia1(self):
    self.opLDA(self.IndirectXAddr)
    self.pc+=1

  @instruction(0xa2, 2, 0)
  def ia2(self):
    self.x=self.ImmediateByte()
    self.FlagsNZ(self.x)
    self.pc+=1

  @instruction(0xa4, 3, 0)
  def ia4(self):
    self.opLDY(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0xa5, 3, 0)
  def ia5(self):
    self.opLDA(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0xa6, 3, 0)
  def ia6(self):
    self.opLDX(self.ZeroPageAddr)
    self.pc+=1
  
  @instruction(0xa8, 2, 0)
  def ia8(self):
    self.y = self.a
    self.FlagsNZ(self.y)

  @instruction(0xa9, 2, 0)
  def ia9(self):
    self.a = self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1

  @instruction(0xaa, 2, 0)
  def iaa(self):
    self.x = self.a
    self.FlagsNZ(self.x)

  @instruction(0xac, 4, 0)
  def iac(self):
    self.opLDY(self.AbsoluteAddr)
    self.pc += 2

  @instruction(0xad, 4, 0)
  def iad(self):
    self.opLDA(self.AbsoluteAddr)
    self.pc += 2

  @instruction(0xae, 4, 0)
  def iae(self):
    self.opLDX(self.AbsoluteAddr)
    self.pc += 2
  
  @instruction(0xb0, 2, 2)
  def ib0(self):
    self.opBST(self.CARRY)
  
  @instruction(0xb1, 5, 1)
  def ib1(self):
    self.opLDA(self.IndirectYAddr)
    self.pc+=1

  @instruction(0xb4, 4, 0)
  def ib4(self):
    self.opLDY(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(0xb5, 4, 0)
  def ib5(self):
    self.opLDA(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(0xb6, 4, 0)
  def ib6(self):
    self.opLDX(self.ZeroPageYAddr)
    self.pc+=1

  @instruction(0xb8, 2, 0)
  def ib8(self):
    self.opCLR(self.OVERFLOW)

  @instruction(0xb9, 4, 1)
  def ib9(self):
    self.opLDA(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(0xba, 2, 0)
  def iba(self):
    self.x = self.sp
    self.FlagsNZ(self.x)
    
  @instruction(0xbc, 4, 1)
  def ibc(self):
    self.opLDY(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0xbd, 4, 1)
  def ibd(self):
    self.opLDA(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0xbe, 4, 1)
  def ibe(self):
    self.opLDX(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(0xc0, 2, 0)
  def ic0(self):
    tbyte = self.ImmediateByte()
    self.flags &= ~(self.CARRY+self.ZERO+self.NEGATIVE)
    if self.y == tbyte:
      self.flags |= self.CARRY+self.ZERO
    elif self.y > tbyte:
      self.flags |= self.CARRY
    else:
      self.flags |= self.NEGATIVE
    self.pc += 1

  @instruction(0xc1, 6, 0)
  def ic1(self):
    self.opCMP(self.IndirectXAddr)
    self.pc+=1

  @instruction(0xc4, 3, 0)
  def ic4(self):
    self.opCPY(self.ZeroPageAddr)
    self.pc += 1

  @instruction(0xc5, 3, 0)
  def ic5(self):
    self.opCMP(self.ZeroPageAddr)
    self.pc += 1

  @instruction(0xc6, 5, 0)
  def ic6(self):
    self.opDECR(self.ZeroPageAddr)
    self.pc += 1

  @instruction(0xc8, 2, 0)
  def ic8(self):
    self.y += 1
    self.y &= 255
    self.FlagsNZ(self.y)

  @instruction(0xc9, 2, 0)
  def ic9(self):
    tbyte = self.ImmediateByte()
    self.flags &= ~(self.CARRY+self.ZERO+self.NEGATIVE)
    if self.a == tbyte:
      self.flags |= self.CARRY + self.ZERO
    elif self.a > tbyte:
      self.flags |= self.CARRY
    else:
      self.flags |= self.NEGATIVE
    self.pc +=1

  @instruction(0xca, 2, 0)
  def ica(self):
    self.x -= 1
    self.x &= 255
    self.FlagsNZ(self.x)

  @instruction(0xcc, 4, 0)
  def icc(self):
    self.opCPY(self.AbsoluteAddr)
    self.pc += 2

  @instruction(0xcd, 4, 0)
  def icd(self):
    self.opCMP(self.AbsoluteAddr)
    self.pc += 2

  @instruction(0xce, 3, 0)
  def ice(self):
    self.opDECR(self.AbsoluteAddr)
    self.pc += 2
  
  @instruction(0xd0, 2, 2)
  def id0(self):
    self.opBCL(self.ZERO)

  @instruction(0xd1, 5, 1)
  def id1(self):
    self.opCMP(self.IndirectYAddr)
    self.pc+=1
  
  @instruction(0xd5, 4, 0)
  def id5(self):
    self.opCMP(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(0xd6, 6, 0)
  def id6(self):
    self.opDECR(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(0xd8, 2, 0)
  def id8(self):
    self.opCLR(self.DECIMAL)

  @instruction(0xd9, 4, 1)
  def id9(self):
    self.opCMP(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(0xdd, 4, 1)
  def idd(self):
    self.opCMP(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0xde, 7, 0)
  def ide(self):
    self.opDECR(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0xe0, 2, 0)
  def ie0(self):
    tbyte = self.ImmediateByte()
    self.flags &= ~(self.CARRY+self.ZERO+self.NEGATIVE)
    if self.x == tbyte:
      self.flags |= self.CARRY + self.ZERO
    elif self.x > tbyte:
      self.flags |= self.CARRY
    else:
      self.flags |= self.NEGATIVE
    self.pc += 1

  @instruction(0xe1, 6, 0)
  def ie1(self):
    self.opSBC(self.IndirectXAddr)
    self.pc+=1
  
  @instruction(0xe4, 3, 0)
  def ie4(self):
    self.opCPX(self.ZeroPageAddr)
    self.pc+=1
  
  @instruction(0xe5, 3, 0)
  def ie5(self):
    self.opSBC(self.ZeroPageAddr)
    self.pc+=1

  @instruction(0xe6, 5, 0)
  def ie6(self):
    self.opINCR(self.ZeroPageAddr)
    self.pc+=1
  
  @instruction(0xe8, 2, 0)
  def ie8(self):
    self.x+=1
    self.x&=255 
    self.FlagsNZ(self.x)
  
  @instruction(0xe9, 2, 0)
  def ie9(self):
    data=self.ImmediateByte()

    if self.flags & self.DECIMAL:
      if self.flags & self.CARRY:
        tmp = 0
      else:
        tmp = 1
      data = convert_to_bin(self.a) - convert_to_bin(data) - tmp
      self.flags &= ~(self.CARRY+self.ZERO+self.NEGATIVE+self.OVERFLOW)
      if data == 0:
        self.flags |= self.ZERO + self.CARRY
      elif data > 0:
        self.flags |= self.CARRY
      else:
        self.flags |= self.NEGATIVE
        data +=100
      self.a = convert_to_bcd(data)
    else:
      if self.flags & self.CARRY:
        tmp = 0
      else:
        tmp = 1    
      data = self.a - data - tmp
      self.flags &= ~(self.CARRY+self.ZERO+self.OVERFLOW+self.NEGATIVE)
      if data == 0:
        self.flags |= self.ZERO + self.CARRY
      elif data > 0:
        self.flags |= self.CARRY
      else:
        self.flags |= self.OVERFLOW
      data &= 255
      self.flags |= data & 128
      self.a = data
    self.pc += 1

  @instruction(0xea, 2, 0)
  def iea(self):
    pass

  @instruction(0xec, 4, 0)
  def iec(self):
    self.opCPX(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(0xed, 4, 0)
  def ied(self):
    self.opSBC(self.AbsoluteAddr)
    self.pc+=2

  @instruction(0xee, 6, 0)
  def iee(self):
    self.opINCR(self.AbsoluteAddr)
    self.pc+=2

  @instruction(0xf0, 2, 2)
  def if0(self):
    self.opBST(self.ZERO)

  @instruction(0xf1, 5, 1)
  def if1(self):
    self.opSBC(self.IndirectYAddr)
    self.pc+=1

  @instruction(0xf5, 4, 0)
  def if5(self):
    self.opSBC(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(0xf6, 6, 0)
  def if6(self):
    self.opINCR(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(0xf8, 2, 0)
  def if8(self):
    self.opSET(self.DECIMAL)
  
  @instruction(0xf9, 4, 1)
  def if9(self):
    self.opSBC(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(0xfd, 4, 1)
  def ifd(self):
    self.opSBC(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(0xfe, 7, 0)  
  def ife(self):
    self.opINCR(self.AbsoluteXAddr)
    self.pc+=2

