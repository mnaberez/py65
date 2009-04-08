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
  disassemble = [('???', 'imp')] * 256

  instruction = make_instruction_decorator(instruct, disassemble, 
                                                cycletime, extracycles)

  @instruction(name="BRK", mode="imp", cycles=7)
  def i00(self):
    pc = (self.pc + 2) & 0xFFFF
    self.stPushWord(pc)

    self.flags |= self.BREAK
    self.stPush(self.flags)

    self.flags |= self.INTERRUPT
    self.pc = self.WordAt(self.IrqTo)

    self.breakFlag = True

  @instruction(name="ORA", mode="inx", cycles=6)
  def i01(self):
    self.opORA(self.IndirectXAddr)
    self.pc += 1

  @instruction(name="ORA", mode="zpg", cycles=3)
  def i05(self):
    self.opORA(self.ZeroPageAddr)
    self.pc += 1

  @instruction(name="ASL", mode="zpg", cycles=5)
  def i06(self):
    self.opASL(self.ZeroPageAddr)
    self.pc += 1
  
  @instruction(name="PHP", mode="imp", cycles=3)
  def i08(self):
    self.stPush(self.flags)
  
  @instruction(name="ORA", mode="imm", cycles=2)
  def i09(self):
    self.a |= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1
  
  @instruction(name="ASL", mode="acc", cycles=2)
  def i0a(self):
    if self.a & 128:
      self.flags |= self.CARRY
    else:
      self.flags &= ~self.CARRY
    self.a = self.a << 1
    self.FlagsNZ(self.a)
    self.a &= 255

  @instruction(name="ORA", mode="abs", cycles=4)
  def i0d(self):
    self.opORA(self.AbsoluteAddr)
    self.pc += 2
  
  @instruction(name="ASL", mode="abs", cycles=6)
  def i0e(self):
    self.opASL(self.AbsoluteAddr)
    self.pc += 2
  
  @instruction(name="BPL", mode="rel", cycles=2, extracycles=2)
  def i10(self):
    self.opBCL(self.NEGATIVE)
  
  @instruction(name="ORA", mode="iny", cycles=5, extracycles=1)
  def i11(self):
    self.opORA(self.IndirectYAddr)
    self.pc += 1
  
  @instruction(name="ORA", mode="zpx", cycles=4)
  def i15(self):
    self.opORA(self.ZeroPageXAddr)
    self.pc += 1
  
  @instruction(name="ASL", mode="zpx", cycles=6)
  def i16(self):
    self.opASL(self.ZeroPageXAddr)
    self.pc += 1
  
  @instruction(name="CLC", mode="imp", cycles=2)
  def i18(self):
    self.opCLR(self.CARRY)
  
  @instruction(name="ORA", mode="aby", cycles=4, extracycles=1)
  def i19(self):
    self.opORA(self.AbsoluteYAddr)
    self.pc += 2 
  
  @instruction(name="ORA", mode="abx", cycles=4, extracycles=1)
  def i1d(self):
    self.opORA(self.AbsoluteXAddr)
    self.pc += 2

  @instruction(name="ASL", mode="abx", cycles=7)
  def i1e(self):
    self.opASL(self.AbsoluteXAddr)
    self.pc += 2

  @instruction(name="JSR", mode="abs", cycles=6)
  def i20(self): 
    self.stPushWord((self.pc+1)&0xffff)
    self.pc=self.WordAt(self.pc)
  
  @instruction(name="AND", mode="inx", cycles=6)
  def i21(self):
    self.opAND(self.IndirectXAddr)
    self.pc += 1
  
  @instruction(name="BIT", mode="zpg", cycles=3)
  def i24(self):
    self.opBIT(self.ZeroPageAddr)
    self.pc += 1
  
  @instruction(name="AND", mode="zpg", cycles=3)
  def i25(self):
    self.opAND(self.ZeroPageAddr)
    self.pc += 1
  
  @instruction(name="ROL", mode="zpg", cycles=5)
  def i26(self):
    self.opROL(self.ZeroPageAddr)
    self.pc += 1

  @instruction(name="PLP", mode="imp", cycles=4)
  def i28(self):
    self.flags = self.stPop()
  
  @instruction(name="AND", mode="imm", cycles=2)
  def i29(self):
    self.a &= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1

  @instruction(name="ROL", mode="acc", cycles=2)
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

  @instruction(name="BIT", mode="abs", cycles=4)
  def i2c(self):
    self.opBIT(self.AbsoluteAddr)
    self.pc+=2

  @instruction(name="AND", mode="abs", cycles=4)
  def i2d(self):
    self.opAND(self.AbsoluteAddr)
    self.pc+=2

  @instruction(name="ROL", mode="abs", cycles=6)
  def i2e(self):
    self.opROL(self.AbsoluteAddr)
    self.pc += 2

  @instruction(name="BMI", mode="rel", cycles=2, extracycles=2)
  def i30(self):
    self.opBST(self.NEGATIVE)

  @instruction(name="AND", mode="iny", cycles=5, extracycles=1)
  def i31(self):
    self.opAND(self.IndirectYAddr)
    self.pc += 1

  @instruction(name="AND", mode="zpx", cycles=4)
  def i35(self):
    self.opAND(self.ZeroPageXAddr)
    self.pc += 1

  @instruction(name="ROL", mode="zpx", cycles=6)
  def i36(self):
    self.opROL(self.ZeroPageXAddr)
    self.pc += 1

  @instruction(name="SEC", mode="imp", cycles=2)
  def i38(self):
    self.opSET(self.CARRY)

  @instruction(name="AND", mode="aby", cycles=4, extracycles=1)
  def i39(self):
    self.opAND(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(name="AND", mode="abx", cycles=4, extracycles=1)
  def i3d(self):
    self.opAND(self.AbsoluteXAddr)
    self.pc += 2 

  @instruction(name="ROL", mode="abx", cycles=7)
  def i3e(self):
    self.opROL(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="RTI", mode="imp", cycles=6)
  def i40(self):
    self.flags = self.stPop()
    self.pc = self.stPopWord()

  @instruction(name="EOR", mode="inx", cycles=6)
  def i41(self):
    self.opEOR(self.IndirectXAddr)
    self.pc+=1

  @instruction(name="EOR", mode="zpg", cycles=3)
  def i45(self):
    self.opEOR(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="LSR", mode="zpg", cycles=5)
  def i46(self):
    self.opLSR(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="PHA", mode="imp", cycles=3)
  def i48(self):
    self.stPush(self.a)

  @instruction(name="EOR", mode="imm", cycles=2)
  def i49(self):
    self.a ^= self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc+=1

  @instruction(name="LSR", mode="acc", cycles=2)
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

  @instruction(name="JMP", mode="abs", cycles=3)
  def i4c(self):
    self.pc=self.WordAt(self.pc)

  @instruction(name="EOR", mode="abs", cycles=4)
  def i4d(self):
    self.opEOR(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(name="LSR", mode="abs", cycles=6)
  def i4e(self):
    self.opLSR(self.AbsoluteAddr)
    self.pc += 2

  @instruction(name="BVC", mode="rel", cycles=2, extracycles=2)
  def i50(self):
    self.opBCL(self.OVERFLOW)

  @instruction(name="EOR", mode="iny", cycles=5, extracycles=1)
  def i51(self):
    self.opEOR(self.IndirectYAddr)
    self.pc+=1

  @instruction(name="EOR", mode="zpx", cycles=4)
  def i55(self):
    self.opEOR(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(name="LSR", mode="zpx", cycles=6)
  def i56(self):
    self.opLSR(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(name="CLI", mode="imp", cycles=2)
  def i58(self):
    self.opCLR(self.INTERRUPT)

  @instruction(name="EOR", mode="aby", cycles=4, extracycles=1)
  def i59(self):
    self.opEOR(self.AbsoluteYAddr)
    self.pc +=2

  @instruction(name="EOR", mode="abx", cycles=4, extracycles=1)
  def i5d(self):
    self.opEOR(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="LSR", mode="abx", cycles=7)
  def i5e(self):
    self.opLSR(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="RTS", mode="imp", cycles=6)
  def i60(self):
    self.pc=self.stPopWord()
    self.pc+=1

  @instruction(name="ADC", mode="inx", cycles=6)
  def i61(self):
    self.opADC(self.IndirectXAddr)
    self.pc+=1

  @instruction(name="ADC", mode="zpg", cycles=3)
  def i65(self):
    self.opADC(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="ROR", mode="zpg", cycles=5)
  def i66(self):
    self.opROR(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="PLA", mode="imp", cycles=4)
  def i68(self):
    self.a = self.stPop()
    self.FlagsNZ(self.a)

  @instruction(name="ADC", mode="imm", cycles=2)
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

  @instruction(name="ROR", mode="acc", cycles=2)
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

  @instruction(name="JMP", mode="ind", cycles=5)
  def i6c(self):
    ta = self.WordAt(self.pc)
    self.pc = self.WordAt(ta)

  @instruction(name="ADC", mode="abs", cycles=4)
  def i6d(self):
    self.opADC(self.AbsoluteAddr)
    self.pc +=2 

  @instruction(name="ROR", mode="abs", cycles=6)
  def i6e(self):
    self.opROR(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(name="BVS", mode="rel", cycles=2, extracycles=2)
  def i70(self):
    self.opBST(self.OVERFLOW)

  @instruction(name="ADC", mode="iny", cycles=5, extracycles=1)
  def i71(self):
    self.opADC(self.IndirectYAddr)
    self.pc+=1

  @instruction(name="ADC", mode="zpx", cycles=4)
  def i75(self):
    self.opADC(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(name="ROR", mode="zpx", cycles=6)
  def i76(self):
    self.opROR(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(name="SEI", mode="imp", cycles=2)
  def i78(self):
    self.opSET(self.INTERRUPT)

  @instruction(name="ADC", mode="aby", cycles=4, extracycles=1)
  def i79(self):
    self.opADC(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(name="ADC", mode="abx", cycles=4, extracycles=1)
  def i7d(self):
    self.opADC(self.AbsoluteXAddr)
    self.pc+=2
  
  @instruction(name="ROR", mode="abx", cycles=7)
  def i7e(self):
    self.opROR(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="STA", mode="inx", cycles=6)
  def i81(self):
    self.opSTA(self.IndirectXAddr)
    self.pc+=1

  @instruction(name="STY", mode="zpg", cycles=3)
  def i84(self):
    self.opSTY(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="STA", mode="zpg", cycles=3)
  def i85(self):
    self.opSTA(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="STX", mode="zpg", cycles=3)
  def i86(self):
    self.opSTX(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="DEY", mode="imp", cycles=2)
  def i88(self):
    self.y -= 1
    self.y&=255
    self.FlagsNZ(self.y)
  
  @instruction(name="TXA", mode="imp", cycles=2)
  def i8a(self):
    self.a=self.x
    self.FlagsNZ(self.a)
  
  @instruction(name="STY", mode="abs", cycles=4)
  def i8c(self):
    self.opSTY(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(name="STA", mode="abs", cycles=4)
  def i8d(self):
    self.opSTA(self.AbsoluteAddr)
    self.pc+=2

  @instruction(name="STX", mode="abs", cycles=4)
  def i8e(self):
    self.opSTX(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(name="BCC", mode="rel", cycles=2, extracycles=2)
  def i90(self):
    self.opBCL(self.CARRY)
  
  @instruction(name="STA", mode="iny", cycles=6)
  def i91(self):
    self.opSTA(self.IndirectYAddr)
    self.pc+=1
  
  @instruction(name="STY", mode="zpx", cycles=4)
  def i94(self):
    self.opSTY(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(name="STA", mode="zpx", cycles=4)
  def i95(self):
    self.opSTA(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(name="STX", mode="zpy", cycles=4)
  def i96(self):
    self.opSTX(self.ZeroPageYAddr)
    self.pc+=1
  
  @instruction(name="TYA", mode="imp", cycles=2)
  def i98(self):
    self.a = self.y
    self.FlagsNZ(self.a)
  
  @instruction(name="STA", mode="aby", cycles=5)
  def i99(self):
    self.opSTA(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(name="TXS", mode="imp", cycles=2)
  def i9a(self):
    self.sp=self.x

  @instruction(name="STA", mode="abx", cycles=5)
  def i9d(self):
    self.opSTA(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="LDY", mode="imm", cycles=2)
  def ia0(self):
    self.y=self.ImmediateByte()
    self.FlagsNZ(self.y)
    self.pc+=1

  @instruction(name="LDA", mode="inx", cycles=6)
  def ia1(self):
    self.opLDA(self.IndirectXAddr)
    self.pc+=1

  @instruction(name="LDX", mode="imm", cycles=2)
  def ia2(self):
    self.x=self.ImmediateByte()
    self.FlagsNZ(self.x)
    self.pc+=1

  @instruction(name="LDY", mode="zpg", cycles=3)
  def ia4(self):
    self.opLDY(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="LDA", mode="zpg", cycles=3)
  def ia5(self):
    self.opLDA(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="LDX", mode="zpg", cycles=3)
  def ia6(self):
    self.opLDX(self.ZeroPageAddr)
    self.pc+=1
  
  @instruction(name="TAY", mode="imp", cycles=2)
  def ia8(self):
    self.y = self.a
    self.FlagsNZ(self.y)

  @instruction(name="LDA", mode="imm", cycles=2)
  def ia9(self):
    self.a = self.ImmediateByte()
    self.FlagsNZ(self.a)
    self.pc += 1

  @instruction(name="TAX", mode="imp", cycles=2)
  def iaa(self):
    self.x = self.a
    self.FlagsNZ(self.x)

  @instruction(name="LDY", mode="abs", cycles=4)
  def iac(self):
    self.opLDY(self.AbsoluteAddr)
    self.pc += 2

  @instruction(name="LDA", mode="abs", cycles=4)
  def iad(self):
    self.opLDA(self.AbsoluteAddr)
    self.pc += 2

  @instruction(name="LDX", mode="abs", cycles=4)
  def iae(self):
    self.opLDX(self.AbsoluteAddr)
    self.pc += 2
  
  @instruction(name="BCS", mode="rel", cycles=2, extracycles=2)
  def ib0(self):
    self.opBST(self.CARRY)
  
  @instruction(name="LDA", mode="iny", cycles=5, extracycles=1)
  def ib1(self):
    self.opLDA(self.IndirectYAddr)
    self.pc+=1

  @instruction(name="LDY", mode="zpx", cycles=4)
  def ib4(self):
    self.opLDY(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(name="LDA", mode="zpx", cycles=4)
  def ib5(self):
    self.opLDA(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(name="LDX", mode="zpy", cycles=4)
  def ib6(self):
    self.opLDX(self.ZeroPageYAddr)
    self.pc+=1

  @instruction(name="CLV", mode="imp", cycles=2)
  def ib8(self):
    self.opCLR(self.OVERFLOW)

  @instruction(name="LDA", mode="aby", cycles=4, extracycles=1)
  def ib9(self):
    self.opLDA(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(name="TSX", mode="imp", cycles=2)
  def iba(self):
    self.x = self.sp
    self.FlagsNZ(self.x)
    
  @instruction(name="LDY", mode="abx", cycles=4, extracycles=1)
  def ibc(self):
    self.opLDY(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="LDA", mode="abx", cycles=4, extracycles=1)
  def ibd(self):
    self.opLDA(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="LDX", mode="aby", cycles=4, extracycles=1)
  def ibe(self):
    self.opLDX(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(name="CPY", mode="imm", cycles=2)
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

  @instruction(name="CMP", mode="inx", cycles=6)
  def ic1(self):
    self.opCMP(self.IndirectXAddr)
    self.pc+=1

  @instruction(name="CPY", mode="zpg", cycles=3)
  def ic4(self):
    self.opCPY(self.ZeroPageAddr)
    self.pc += 1

  @instruction(name="CMP", mode="zpg", cycles=3)
  def ic5(self):
    self.opCMP(self.ZeroPageAddr)
    self.pc += 1

  @instruction(name="DEC", mode="zpg", cycles=5)
  def ic6(self):
    self.opDECR(self.ZeroPageAddr)
    self.pc += 1

  @instruction(name="INY", mode="imp", cycles=2)
  def ic8(self):
    self.y += 1
    self.y &= 255
    self.FlagsNZ(self.y)

  @instruction(name="CMP", mode="imm", cycles=2)
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

  @instruction(name="DEX", mode="imp", cycles=2)
  def ica(self):
    self.x -= 1
    self.x &= 255
    self.FlagsNZ(self.x)

  @instruction(name="CPY", mode="abs", cycles=4)
  def icc(self):
    self.opCPY(self.AbsoluteAddr)
    self.pc += 2

  @instruction(name="CMP", mode="abs", cycles=4)
  def icd(self):
    self.opCMP(self.AbsoluteAddr)
    self.pc += 2

  @instruction(name="DEC", mode="abs", cycles=3)
  def ice(self):
    self.opDECR(self.AbsoluteAddr)
    self.pc += 2
  
  @instruction(name="BNE", mode="rel", cycles=2, extracycles=2)
  def id0(self):
    self.opBCL(self.ZERO)

  @instruction(name="CMP", mode="iny", cycles=5, extracycles=1)
  def id1(self):
    self.opCMP(self.IndirectYAddr)
    self.pc+=1
  
  @instruction(name="CMP", mode="zpx", cycles=4)
  def id5(self):
    self.opCMP(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(name="DEC", mode="zpx", cycles=6)
  def id6(self):
    self.opDECR(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(name="CLD", mode="imp", cycles=2)
  def id8(self):
    self.opCLR(self.DECIMAL)

  @instruction(name="CMP", mode="aby", cycles=4, extracycles=1)
  def id9(self):
    self.opCMP(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(name="CMP", mode="abx", cycles=4, extracycles=1)
  def idd(self):
    self.opCMP(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="DEC", mode="abx", cycles=7)
  def ide(self):
    self.opDECR(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="CPX", mode="imm", cycles=2)
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

  @instruction(name="SBC", mode="inx", cycles=6)
  def ie1(self):
    self.opSBC(self.IndirectXAddr)
    self.pc+=1
  
  @instruction(name="CPX", mode="zpg", cycles=3)
  def ie4(self):
    self.opCPX(self.ZeroPageAddr)
    self.pc+=1
  
  @instruction(name="SBC", mode="zpg", cycles=3)
  def ie5(self):
    self.opSBC(self.ZeroPageAddr)
    self.pc+=1

  @instruction(name="INC", mode="zpg", cycles=5)
  def ie6(self):
    self.opINCR(self.ZeroPageAddr)
    self.pc+=1
  
  @instruction(name="INX", mode="imp", cycles=2)
  def ie8(self):
    self.x+=1
    self.x&=255 
    self.FlagsNZ(self.x)
  
  @instruction(name="SBC", mode="imm", cycles=2)
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

  @instruction(name="NOP", mode="imp", cycles=2)
  def iea(self):
    pass

  @instruction(name="CPX", mode="abs", cycles=4)
  def iec(self):
    self.opCPX(self.AbsoluteAddr)
    self.pc+=2
  
  @instruction(name="SBC", mode="abs", cycles=4)
  def ied(self):
    self.opSBC(self.AbsoluteAddr)
    self.pc+=2

  @instruction(name="INC", mode="abs", cycles=6)
  def iee(self):
    self.opINCR(self.AbsoluteAddr)
    self.pc+=2

  @instruction(name="BEQ", mode="rel", cycles=2, extracycles=2)
  def if0(self):
    self.opBST(self.ZERO)

  @instruction(name="SBC", mode="iny", cycles=5, extracycles=1)
  def if1(self):
    self.opSBC(self.IndirectYAddr)
    self.pc+=1

  @instruction(name="SBC", mode="zpx", cycles=4)
  def if5(self):
    self.opSBC(self.ZeroPageXAddr)
    self.pc+=1

  @instruction(name="INC", mode="zpx", cycles=6)
  def if6(self):
    self.opINCR(self.ZeroPageXAddr)
    self.pc+=1
  
  @instruction(name="SED", mode="imp", cycles=2)
  def if8(self):
    self.opSET(self.DECIMAL)
  
  @instruction(name="SBC", mode="aby", cycles=4, extracycles=1)
  def if9(self):
    self.opSBC(self.AbsoluteYAddr)
    self.pc+=2

  @instruction(name="SBC", mode="abx", cycles=4, extracycles=1)
  def ifd(self):
    self.opSBC(self.AbsoluteXAddr)
    self.pc+=2

  @instruction(name="INC", mode="abx", cycles=7)  
  def ife(self):
    self.opINCR(self.AbsoluteXAddr)
    self.pc+=2

