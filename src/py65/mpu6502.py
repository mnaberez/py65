from py65 import util

class MPU:
  # vectors
  ResetTo = 0xfffc
  IrqTo   = 0xfffe
  NMITo   = 0xfffa

  # processor flags
  NEGATIVE  = 128
  OVERFLOW  = 64
  BREAK     = 16
  DECIMAL   = 8
  INTERRUPT = 4
  ZERO      = 2
  CARRY     = 1

  def __init__(self):
    # config
    self.debug = False
    
    # vm status
    self.breakFlag = False
    self.excycles = 0
    self.addcycles = False
    self.processorCycles = 0
    self.internalCycleDelay = 0

    # init
    self.clearMemory()
    self.reset()

  def __repr__(self):
    out = '<6502: A=%02x, X=%02x, Y=%02x, Flags=%02x, SP=%02x, PC=%04x>'
    return out % (self.a, self.x, self.y,
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
    self.pc=0
    self.sp=255
    self.a=self.x=self.y=0
    self.flags=32
    self.breakFlag=False
    self.processorCycles=0

  def clearMemory(self, start=0x0000, end=0xFFFF):
    self.memory = [] 
    for addr in range(start, end + 1):
      self.memory.insert(addr, 0x00)

  def ByteAt(self, addr):
    return self.memory[addr]

  def WordAt(self, addr):
    return self.ByteAt(addr) + (self.ByteAt(addr + 1) << 8)

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
      data = util.convert_to_bin(data) + util.convert_to_bin(self.a) + tmp
      self.flags &= ~(self.CARRY+self.OVERFLOW+self.NEGATIVE+self.ZERO)
      if data > 99:
        self.flags |= self.CARRY + self.OVERFLOW
        data -= 100

      if data == 0:
        self.flags |= self.ZERO
      else:
        self.flags |= data & 128
      self.a = util.convert_to_bcd(data)
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
    
      data = util.convert_to_bin(self.a) - util.convert_to_bin(data) - borrow
      self.flags &= ~(self.CARRY + self.ZERO + self.NEGATIVE + self.OVERFLOW)
      if data == 0:
        self.flags |= self.ZERO + self.CARRY
      elif data > 0:
        self.flags |= self.CARRY
      else:
        self.flags |= self.NEGATIVE
        data +=100
      self.a = util.convert_to_bcd(data)
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

  def i00(self):
    pc = (self.pc + 2) & 0xFFFF
    self.stPushWord(pc)

    self.flags |= self.BREAK
    self.stPush(self.flags)

    self.flags |= self.INTERRUPT
    self.pc = self.WordAt(self.IrqTo)

    self.breakFlag = True

  def i01(self):
    self.opORA(self.IndirectXAddr)
    self.pc += 1

  def i05(self):
    self.opORA(self.ZeroPageAddr)
    self.pc += 1

  def i06(self):
    self.opASL(self.ZeroPageAddr)
    self.pc += 1
  
  def i08(self):
    self.stPush(self.flags)
  
  def i09(self):
    self.a |= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1
  
  def i0a(self):
    if self.a & 128:
      self.flags |= self.CARRY
    else:
      self.flags &= ~self.CARRY
    self.a = self.a << 1
    self.FlagsNZ(self.a)
    self.a &= 255

  def i0d(self):
    self.opORA(self.AbsoluteAddr)
    self.pc += 2
  
  def i0e(self):
    self.opASL(self.AbsoluteAddr)
    self.pc += 2
  
  def i10(self):
    self.opBCL(self.NEGATIVE)
  
  def i11(self):
    self.opORA(self.IndirectYAddr)
    self.pc += 1
  
  def i15(self):
    self.opORA(self.ZeroPageXAddr)
    self.pc += 1
  
  def i16(self):
    self.opASL(self.ZeroPageXAddr)
    self.pc += 1
  
  def i18(self):
    self.opCLR(self.CARRY)
  
  def i19(self):
    self.opORA(self.AbsoluteYAddr)
    self.pc += 2 
  
  def i1d(self):
    self.opORA(self.AbsoluteXAddr)
    self.pc += 2

  def i1e(self):
    self.opASL(self.AbsoluteXAddr)
    self.pc += 2
  
  def i20(self): 
    self.stPushWord((self.pc+1)&0xffff)
    self.pc=self.WordAt(self.pc)
  
  def i21(self):
    self.opAND(self.IndirectXAddr)
    self.pc += 1
  
  def i24(self):
    self.opBIT(self.ZeroPageAddr)
    self.pc += 1
  
  def i25(self):
    self.opAND(self.ZeroPageAddr)
    self.pc += 1
  
  def i26(self):
    self.opROL(self.ZeroPageAddr)
    self.pc += 1

  def i28(self):
    self.flags = self.stPop()
  
  def i29(self):
    self.a &= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1

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

  def i2c(self):
    self.opBIT(self.AbsoluteAddr)
    self.pc+=2

  def i2d(self):
    self.opAND(self.AbsoluteAddr)
    self.pc+=2

  def i2e(self):
    self.opROL(self.AbsoluteAddr)
    self.pc += 2

  def i30(self):
    self.opBST(self.NEGATIVE)

  def i31(self):
    self.opAND(self.IndirectYAddr)
    self.pc += 1

  def i35(self):
    self.opAND(self.ZeroPageXAddr)
    self.pc += 1

  def i36(self):
    self.opROL(self.ZeroPageXAddr)
    self.pc += 1

  def i38(self):
    self.opSET(self.CARRY)

  def i39(self):
    self.opAND(self.AbsoluteYAddr)
    self.pc+=2

  def i3d(self):
    self.opAND(self.AbsoluteXAddr)
    self.pc += 2 

  def i3e(self):
    self.opROL(self.AbsoluteXAddr)
    self.pc+=2

  def i40(self):
    self.flags = self.stPop()
    self.pc = self.stPopWord()

  def i41(self):
    self.opEOR(self.IndirectXAddr)
    self.pc+=1

  def i45(self):
    self.opEOR(self.ZeroPageAddr)
    self.pc+=1

  def i46(self):
    self.opLSR(self.ZeroPageAddr)
    self.pc+=1

  def i48(self):
    self.stPush(self.a)

  def i49(self):
    self.a ^= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc+=1

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

  def i4c(self):
    self.pc=self.WordAt(self.pc)

  def i4d(self):
    self.opEOR(self.AbsoluteAddr)
    self.pc+=2
  
  def i4e(self):
    self.opLSR(self.AbsoluteAddr)
    self.pc += 2

  def i50(self):
    self.opBCL(self.OVERFLOW)

  def i51(self):
    self.opEOR(self.IndirectYAddr)
    self.pc+=1

  def i55(self):
    self.opEOR(self.ZeroPageXAddr)
    self.pc+=1

  def i56(self):
    self.opLSR(self.ZeroPageXAddr)
    self.pc+=1

  def i58(self):
    self.opCLR(self.INTERRUPT)

  def i59(self):
    self.opEOR(self.AbsoluteYAddr)
    self.pc +=2

  def i5d(self):
    self.opEOR(self.AbsoluteXAddr)
    self.pc+=2

  def i5e(self):
    self.opLSR(self.AbsoluteXAddr)
    self.pc+=2

  def i60(self):
    self.pc=self.stPopWord()
    self.pc+=1

  def i61(self):
    self.opADC(self.IndirectXAddr)
    self.pc+=1

  def i65(self):
    self.opADC(self.ZeroPageAddr)
    self.pc+=1

  def i66(self):
    self.opROR(self.ZeroPageAddr)
    self.pc+=1

  def i68(self):
    self.a = self.stPop()
    self.FlagsNZ(self.a)

  def i69(self):
    data = self.ImmediateByte()

    if self.flags & self.CARRY:
      tmp = 1
    else:
      tmp = 0

    if self.flags & self.DECIMAL:
      data = util.convert_to_bin(data) + util.convert_to_bin(self.a) + tmp
      self.flags &= ~(self.CARRY+self.OVERFLOW+self.NEGATIVE+self.ZERO)
      if data > 99:
        self.flags |= self.CARRY+self.OVERFLOW
        data -= 100
      if data == 0:
        self.flags |= self.ZERO
      else:
        self.flags |= self.data & 128
      self.a = util.convert_to_bcd(data)
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

  def i6c(self):
    ta = self.WordAt(self.pc)
    self.pc = self.WordAt(ta)

  def i6d(self):
    self.opADC(self.AbsoluteAddr)
    self.pc +=2 

  def i6e(self):
    self.opROR(self.AbsoluteAddr)
    self.pc+=2
  
  def i70(self):
    self.opBST(self.OVERFLOW)

  def i71(self):
    self.opADC(self.IndirectYAddr)
    self.pc+=1

  def i75(self):
    self.opADC(self.ZeroPageXAddr)
    self.pc+=1
  
  def i76(self):
    self.opROR(self.ZeroPageXAddr)
    self.pc+=1
  
  def i78(self):
    self.opSET(self.INTERRUPT)

  def i79(self):
    self.opADC(self.AbsoluteYAddr)
    self.pc+=2

  def i7d(self):
    self.opADC(self.AbsoluteXAddr)
    self.pc+=2
  
  def i7e(self):
    self.opROR(self.AbsoluteXAddr)
    self.pc+=2

  def i81(self):
    self.opSTA(self.IndirectXAddr)
    self.pc+=1

  def i84(self):
    self.opSTY(self.ZeroPageAddr)
    self.pc+=1

  def i85(self):
    self.opSTA(self.ZeroPageAddr)
    self.pc+=1

  def i86(self):
    self.opSTX(self.ZeroPageAddr)
    self.pc+=1

  def i88(self):
    self.y -= 1
    self.y&=255
    self.FlagsNZ(self.y)
  
  def i8a(self):
    self.a=self.x
    self.FlagsNZ(self.a)
  
  def i8c(self):
    self.opSTY(self.AbsoluteAddr)
    self.pc+=2
  
  def i8d(self):
    self.opSTA(self.AbsoluteAddr)
    self.pc+=2

  def i8e(self):
    self.opSTX(self.AbsoluteAddr)
    self.pc+=2
  
  def i90(self):
    self.opBCL(self.CARRY)
  
  def i91(self):
    self.opSTA(self.IndirectYAddr)
    self.pc+=1
  
  def i94(self):
    self.opSTY(self.ZeroPageXAddr)
    self.pc+=1
  
  def i95(self):
    self.opSTA(self.ZeroPageXAddr)
    self.pc+=1
  
  def i96(self):
    self.opSTX(self.ZeroPageYAddr)
    self.pc+=1
  
  def i98(self):
    self.a = self.y
    self.FlagsNZ(self.a)
  
  def i99(self):
    self.opSTA(self.AbsoluteYAddr)
    self.pc+=2

  def i9a(self):
    self.sp=self.x

  def i9d(self):
    self.opSTA(self.AbsoluteXAddr)
    self.pc+=2

  def ia0(self):
    self.y=self.ImmediateByte()
    self.FlagsNZ(self.y)
    self.pc+=1

  def ia1(self):
    self.opLDA(self.IndirectXAddr)
    self.pc+=1

  def ia2(self):
    self.x=self.ImmediateByte()
    self.FlagsNZ(self.x)
    self.pc+=1

  def ia4(self):
    self.opLDY(self.ZeroPageAddr)
    self.pc+=1

  def ia5(self):
    self.opLDA(self.ZeroPageAddr)
    self.pc+=1

  def ia6(self):
    self.opLDX(self.ZeroPageAddr)
    self.pc+=1
  
  def ia8(self):
    self.y = self.a
    self.FlagsNZ(self.y)

  def ia9(self):
    self.a = self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1

  def iaa(self):
    self.x = self.a
    self.FlagsNZ(self.x)

  def iac(self):
    self.opLDY(self.AbsoluteAddr)
    self.pc += 2

  def iad(self):
    self.opLDA(self.AbsoluteAddr)
    self.pc += 2

  def iae(self):
    self.opLDX(self.AbsoluteAddr)
    self.pc += 2
  
  def ib0(self):
    self.opBST(self.CARRY)
  
  def ib1(self):
    self.opLDA(self.IndirectYAddr)
    self.pc+=1

  def ib4(self):
    self.opLDY(self.ZeroPageXAddr)
    self.pc+=1

  def ib5(self):
    self.opLDA(self.ZeroPageXAddr)
    self.pc+=1

  def ib6(self):
    self.opLDX(self.ZeroPageYAddr)
    self.pc+=1

  def ib8(self):
    self.opCLR(self.OVERFLOW)

  def ib9(self):
    self.opLDA(self.AbsoluteYAddr)
    self.pc+=2

  def iba(self):
    self.x = self.sp
    self.FlagsNZ(self.x)
    
  def ibc(self):
    self.opLDY(self.AbsoluteXAddr)
    self.pc+=2

  def ibd(self):
    self.opLDA(self.AbsoluteXAddr)
    self.pc+=2

  def ibe(self):
    self.opLDX(self.AbsoluteYAddr)
    self.pc+=2

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

  def ic1(self):
    self.opCMP(self.IndirectXAddr)
    self.pc+=1

  def ic4(self):
    self.opCPY(self.ZeroPageAddr)
    self.pc += 1

  def ic5(self):
    self.opCMP(self.ZeroPageAddr)
    self.pc += 1

  def ic6(self):
    self.opDECR(self.ZeroPageAddr)
    self.pc += 1

  def ic8(self):
    self.y += 1
    self.y &= 255
    self.FlagsNZ(self.y)

  def ic9(self):
    tbyte = self.ImmediateByte()
    self.flags &= ~(self.CARRY+self.ZERO+self.NEGATIVE)
    if self.a == tbyte:
      self.flags |= self.CARRY + self.ZERO
    elif a > tbyte:
      self.flags |= self.CARRY
    else:
      self.flags |= self.NEGATIVE
    self.pc +=1

  def ica(self):
    self.x -= 1
    self.x &= 255
    self.FlagsNZ(self.x)

  def icc(self):
    self.opCPY(self.AbsoluteAddr)
    self.pc += 2

  def icd(self):
    self.opCMP(self.AbsoluteAddr)
    self.pc += 2

  def ice(self):
    self.opDECR(self.AbsoluteAddr)
    self.pc += 2
  
  def id0(self):
    self.opBCL(self.ZERO)

  def id1(self):
    self.opCMP(self.IndirectYAddr)
    self.pc+=1
  
  def id5(self):
    self.opCMP(self.ZeroPageXAddr)
    self.pc+=1

  def id6(self):
    self.opDECR(self.ZeroPageXAddr)
    self.pc+=1

  def id8(self):
    self.opCLR(self.DECIMAL)

  def id9(self):
    self.opCMP(self.AbsoluteYAddr)
    self.pc+=2

  def idd(self):
    self.opCMP(self.AbsoluteXAddr)
    self.pc+=2

  def ide(self):
    self.opDECR(self.AbsoluteXAddr)
    self.pc+=2

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

  def ie1(self):
    self.opSBC(self.IndirectXAddr)
    self.pc+=1
  
  def ie4(self):
    self.opCPX(self.ZeroPageAddr)
    self.pc+=1
  
  def ie5(self):
    self.opSBC(self.ZeroPageAddr)
    self.pc+=1

  def ie6(self):
    self.opINCR(self.ZeroPageAddr)
    self.pc+=1
  
  def ie8(self):
    self.x+=1
    self.x&=255 
    self.FlagsNZ(self.x)
  
  def ie9(self):
    data=self.ImmediateByte()

    if self.flags & self.DECIMAL:
      if self.flags & self.CARRY:
        tmp = 0
      else:
        tmp = 1
      data = util.convert_to_bin(self.a) - util.convert_to_bin(data) - tmp
      self.flags &= ~(self.CARRY+self.ZERO+self.NEGATIVE+self.OVERFLOW)
      if data == 0:
        self.flags |= self.ZERO + self.CARRY
      elif data > 0:
        self.flags |= self.CARRY
      else:
        self.flags |= self.NEGATIVE
        data +=100
      self.a = util.convert_to_bcd(data)
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

  def iea(self):
    pass

  def iec(self):
    self.opCPX(self.AbsoluteAddr)
    self.pc+=2
  
  def ied(self):
    self.opSBC(self.AbsoluteAddr)
    self.pc+=2

  def iee(self):
    self.opINCR(self.AbsoluteAddr)
    self.pc+=2

  def if0(self):
    self.opBST(self.ZERO)

  def if1(self):
    self.opSBC(self.IndirectYAddr)
    self.pc+=1

  def if5(self):
    self.opSBC(self.ZeroPageXAddr)
    self.pc+=1

  def if6(self):
    self.opINCR(self.ZeroPageXAddr)
    self.pc+=1
  
  def if8(self):
    self.opSET(self.DECIMAL)
  
  def if9(self):
    self.opSBC(self.AbsoluteYAddr)
    self.pc+=2

  def ifd(self):
    self.opSBC(self.AbsoluteXAddr)
    self.pc+=2

  def ife(self):
    self.opINCR(self.AbsoluteXAddr)
    self.pc+=2

  def ini(self):
    if self.debug:
      raise NotImplementedError
    self.pc+=1


  # code pages

  instruct = [
    i00, i01, ini, ini, ini, i05, i06, ini,
    i08, i09, i0a, ini, ini, i0d, i0e, ini,
    i10, i11, ini, ini, ini, i15, i16, ini,
    i18, i19, ini, ini, ini, i1d, i1e, ini,
    i20, i21, ini, ini, i24, i25, i26, ini,
    i28, i29, i2a, ini, i2c, i2d, i2e, ini,
    i30, i31, ini, ini, ini, i35, i36, ini,
    i38, i39, ini, ini, ini, i3d, i3e, ini,
    i40, i41, ini, ini, ini, i45, i46, ini,
    i48, i49, i4a, ini, i4c, i4d, i4e, ini,
    i50, i51, ini, ini, ini, i55, i56, ini,
    i58, i59, ini, ini, ini, i5d, i5e, ini,
    i60, i61, ini, ini, ini, i65, i66, ini,
    i68, i69, i6a, ini, i6c, i6d, i6e, ini,
    i70, i71, ini, ini, ini, i75, i76, ini,
    i78, i79, ini, ini, ini, i7d, i7e, ini,
    ini, i81, ini, ini, i84, i85, i86, ini,
    i88, ini, i8a, ini, i8c, i8d, i8e, ini,
    i90, i91, ini, ini, i94, i95, i96, ini,
    i98, i99, i9a, ini, ini, i9d, ini, ini,
    ia0, ia1, ia2, ini, ia4, ia5, ia6, ini,
    ia8, ia9, iaa, ini, iac, iad, iae, ini,
    ib0, ib1, ini, ini, ib4, ib5, ib6, ini,
    ib8, ib9, iba, ini, ibc, ibd, ibe, ini,
    ic0, ic1, ini, ini, ic4, ic5, ic6, ini,
    ic8, ic9, ica, ini, icc, icd, ice, ini,
    id0, id1, ini, ini, ini, id5, id6, ini,
    id8, id9, ini, ini, ini, idd, ide, ini,
    ie0, ie1, ini, ini, ie4, ie5, ie6, ini,
    ie8, ie9, iea, ini, iec, ied, iee, ini,
    if0, if1, ini, ini, ini, if5, if6, ini,
    if8, if9, ini, ini, ini, ifd, ife, ini
  ]

  cycletime = [
    7, 6, 0, 0, 0, 3, 5, 0, 3, 2, 2, 0, 0, 4, 6, 0,  # 00
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # 10
    6, 6, 0, 0, 3, 3, 5, 0, 4, 2, 2, 0, 4, 4, 6, 0,  # 20
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # 30
    6, 6, 0, 0, 0, 3, 5, 0, 3, 2, 2, 0, 3, 4, 6, 0,  # 40
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # 50
    6, 6, 0, 0, 0, 3, 5, 0, 4, 2, 2, 0, 5, 4, 6, 0,  # 60
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # 70
    0, 6, 0, 0, 3, 3, 3, 0, 2, 0, 2, 0, 4, 4, 4, 0,  # 80
    2, 6, 0, 0, 4, 4, 4, 0, 2, 5, 2, 0, 0, 5, 0, 0,  # 90
    2, 6, 2, 0, 3, 3, 3, 0, 2, 2, 2, 0, 4, 4, 4, 0,  # A0
    2, 5, 0, 0, 4, 4, 4, 0, 2, 4, 2, 0, 4, 4, 4, 0,  # B0
    2, 6, 0, 0, 3, 3, 5, 0, 2, 2, 2, 0, 4, 4, 3, 0,  # C0
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0,  # D0
    2, 6, 0, 0, 3, 3, 5, 0, 2, 2, 2, 0, 4, 4, 6, 0,  # E0
    2, 5, 0, 0, 0, 4, 6, 0, 2, 4, 0, 0, 0, 4, 7, 0   # F0
  ]

  extracycles = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 00
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # 10
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 20
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # 30
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 40
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # 50
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 60
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # 70
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 80
    2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 90
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # A0
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0,  # B0
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # C0
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,  # D0
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # E0
    2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0   # F0
  ]
