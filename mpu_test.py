import unittest
import sys
from mpu import MPU

class MPUTests(unittest.TestCase):
  
  # ADC Absolute
  
  def test_adc_bcd_off_absolute_carry_clear_in_accumulator_zeroes(self):
    cpu = MPU()
    cpu.a = 0
    cpu.memory[0x0000:0x0002] = (0x6D, 0x00, 0xC0) #=> $0000 ADC $C000
    cpu.memory[0xC000] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_absolute_carry_set_in_accumulator_zero(self):
    cpu = MPU()
    cpu.a = 0
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x6D, 0x00, 0xC0) #=> $0000 ADC $C000
    cpu.memory[0xC000] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertNotEquals(cpu.CARRY, cpu.flags & cpu.CARRY)
    
  def test_adc_bcd_off_absolute_carry_clear_in_no_carry_clear_out(self):
    cpu = MPU()
    cpu.a = 0x01
    cpu.memory[0x0000:0x0002] = (0x6D, 0x00, 0xC0) #=> $0000 ADC $C000
    cpu.memory[0xC000] = 0xFE
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_absolute_carry_clear_in_carry_set_out(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.memory[0x0000:0x0002] = (0x6D, 0x00, 0xC0) #=> $0000 ADC $C000
    cpu.memory[0xC000] = 0xFF
    cpu.step()    
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)        
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_absolute_overflow(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0x6D, 0x00, 0xC0) #=> $0000 ADC $C000
    cpu.memory[0xC000] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)    
    self.assertEquals(cpu.OVERFLOW, cpu.flags & cpu.OVERFLOW)       
    self.assertEquals(0, cpu.flags & cpu.ZERO)       

  # ADC Zero Page
  
  def test_adc_bcd_off_zp_carry_clear_in_accumulator_zeroes(self):
    cpu = MPU()
    cpu.a = 0
    cpu.memory[0x0000:0x0001] = (0x65, 0xB0) #=> $0000 ADC $00B0
    cpu.memory[0x00B0] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_absolute_carry_set_in_accumulator_zero(self):
    cpu = MPU()
    cpu.a = 0
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x65, 0xB0) #=> $0000 ADC $00B0
    cpu.memory[0x00B0] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertNotEquals(cpu.CARRY, cpu.flags & cpu.CARRY)
    
  def test_adc_bcd_off_absolute_carry_clear_in_no_carry_clear_out(self):
    cpu = MPU()
    cpu.a = 0x01
    cpu.memory[0x0000:0x0001] = (0x65, 0xB0) #=> $0000 ADC $00B0
    cpu.memory[0x00B0] = 0xFE
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_absolute_carry_clear_in_carry_set_out(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.memory[0x0000:0x0001] = (0x65, 0xB0) #=> $0000 ADC $00B0
    cpu.memory[0x00B0] = 0xFF
    cpu.step()    
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)        
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_absolute_overflow(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0x65, 0xB0) #=> $0000 ADC $00B0
    cpu.memory[0x00B0] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)    
    self.assertEquals(cpu.OVERFLOW, cpu.flags & cpu.OVERFLOW)       
    self.assertEquals(0, cpu.flags & cpu.ZERO)       
      
  # ADC Immediate
  
  def test_adc_bcd_off_immediate_carry_clear_in_accumulator_zeroes(self):
    cpu = MPU()
    cpu.a = 0
    cpu.memory[0x0000:0x0001] = (0x69, 0x00) #=> $0000 ADC #$00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_immediate_carry_set_in_accumulator_zero(self):
    cpu = MPU()
    cpu.a = 0
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x69, 0x00) #=> $0000 ADC #$00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertNotEquals(cpu.CARRY, cpu.flags & cpu.CARRY)
    
  def test_adc_bcd_off_immediate_carry_clear_in_no_carry_clear_out(self):
    cpu = MPU()
    cpu.a = 0x01
    cpu.memory[0x0000:0x0001] = (0x69, 0xFE) #=> $0000 ADC #$FE
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    
  def test_adc_bcd_off_immediate_carry_clear_in_carry_set_out(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.memory[0x0000:0x0001] = (0x69, 0xFF) #=> $0000 ADC #$FF
    cpu.step()    
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)        
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
      
  def test_adc_bcd_off_immediate_overflow(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0001] = (0x69, 0xFF) #=> $0000 ADC #$FF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)    
    self.assertEquals(cpu.OVERFLOW, cpu.flags & cpu.OVERFLOW)       
    self.assertEquals(0, cpu.flags & cpu.ZERO)       

  # ADC Absolute, X-Indexed
  
  def test_adc_bcd_off_abs_x_carry_clear_in_accumulator_zeroes(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x7D, 0x00, 0xC0) #=> $0000 ADC $C000,X
    cpu.memory[0xC000 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_abs_x_carry_set_in_accumulator_zero(self):
    cpu = MPU()
    cpu.a = 0
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x7D, 0x00, 0xC0) #=> $0000 ADC $C000,X
    cpu.memory[0xC000 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertNotEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  def test_adc_bcd_off_abs_x_carry_clear_in_no_carry_clear_out(self):
    cpu = MPU()
    cpu.a = 0x01
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x7D, 0x00, 0xC0) #=> $0000 ADC $C000,X
    cpu.memory[0xC000 + cpu.x] = 0xFE
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_abs_x_carry_clear_in_carry_set_out(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x7D, 0x00, 0xC0) #=> $0000 ADC $C000,X
    cpu.memory[0xC000 + cpu.x] = 0xFF
    cpu.step()    
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)        
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_abs_x_overflow(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x7D, 0x00, 0xC0) #=> $0000 ADC $C000,X
    cpu.memory[0xC000 + cpu.x] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)    
    self.assertEquals(cpu.OVERFLOW, cpu.flags & cpu.OVERFLOW)       
    self.assertEquals(0, cpu.flags & cpu.ZERO)       

  # ADC Absolute, Y-Indexed
  
  def test_adc_bcd_off_abs_y_carry_clear_in_accumulator_zeroes(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x79, 0x00, 0xC0) #=> $0000 ADC $C000,Y
    cpu.memory[0xC000 + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_abs_y_carry_set_in_accumulator_zero(self):
    cpu = MPU()
    cpu.a = 0
    cpu.y = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x7D, 0x00, 0xC0) #=> $0000 ADC $C000,Y
    cpu.memory[0xC000 + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertNotEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  def test_adc_bcd_off_abs_y_carry_clear_in_no_carry_clear_out(self):
    cpu = MPU()
    cpu.a = 0x01
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x79, 0x00, 0xC0) #=> $0000 ADC $C000,Y
    cpu.memory[0xC000 + cpu.y] = 0xFE
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_abs_y_carry_clear_in_carry_set_out(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x79, 0x00, 0xC0) #=> $0000 ADC $C000,Y
    cpu.memory[0xC000 + cpu.y] = 0xFF
    cpu.step()    
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)        
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_abs_y_overflow(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x79, 0x00, 0xC0) #=> $0000 ADC $C000,Y
    cpu.memory[0xC000 + cpu.y] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)    
    self.assertEquals(cpu.OVERFLOW, cpu.flags & cpu.OVERFLOW)       
    self.assertEquals(0, cpu.flags & cpu.ZERO)       

  # ADC Zero Page, X-Indexed
  
  def test_adc_bcd_off_zp_x_carry_clear_in_accumulator_zeroes(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x75, 0x10) #=> $0000 ADC $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_zp_x_carry_set_in_accumulator_zero(self):
    cpu = MPU()
    cpu.a = 0
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x75, 0x10) #=> $0000 ADC $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertNotEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  def test_adc_bcd_off_zp_x_carry_clear_in_no_carry_clear_out(self):
    cpu = MPU()
    cpu.a = 0x01
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x75, 0x10) #=> $0000 ADC $0010,X
    cpu.memory[0x0010 + cpu.x] = 0xFE
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_zp_x_carry_clear_in_carry_set_out(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x75, 0x10) #=> $0000 ADC $0010,X
    cpu.memory[0x0010 + cpu.x] = 0xFF
    cpu.step()    
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)        
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_zp_x_overflow(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x75, 0x10) #=> $0000 ADC $0010,X
    cpu.memory[0x0010 + cpu.x] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)    
    self.assertEquals(cpu.OVERFLOW, cpu.flags & cpu.OVERFLOW)       
    self.assertEquals(0, cpu.flags & cpu.ZERO)       

  # ADC Indirect, Indexed (X)
  
  def test_adc_bcd_off_indirect_indexed_carry_clear_in_accumulator_zeroes(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x61, 0x10) #=> $0000 ADC ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_indirect_indexed_carry_set_in_accumulator_zero(self):
    cpu = MPU()
    cpu.a = 0
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x61, 0x10) #=> $0000 ADC ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertNotEquals(cpu.CARRY, cpu.flags & cpu.CARRY)
  
  def test_adc_bcd_off_indirect_indexed_carry_clear_in_no_carry_clear_out(self):
    cpu = MPU()
    cpu.a = 0x01
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x61, 0x10) #=> $0000 ADC ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0xFE
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_adc_bcd_off_indirect_indexed_carry_clear_in_carry_set_out(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x61, 0x10) #=> $0000 ADC ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0xFF
    cpu.step()    
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)        
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_adc_bcd_off_indirect_indexed_overflow(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x61, 0x10) #=> $0000 ADC ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)    
    self.assertEquals(cpu.OVERFLOW, cpu.flags & cpu.OVERFLOW)       
    self.assertEquals(0, cpu.flags & cpu.ZERO)       

  # ADC Indexed, Indirect (Y)

  def test_adc_bcd_off_indexed_indirect_carry_clear_in_accumulator_zeroes(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x71, 0x10) #=> $0000 ADC ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_adc_bcd_off_indexed_indirect_carry_set_in_accumulator_zero(self):
    cpu = MPU()
    cpu.a = 0
    cpu.y = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x71, 0x10) #=> $0000 ADC ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertNotEquals(cpu.CARRY, cpu.flags & cpu.CARRY)
  
  def test_adc_bcd_off_indexed_indirect_carry_clear_in_no_carry_clear_out(self):
    cpu = MPU()
    cpu.a = 0x01
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x71, 0x10) #=> $0000 ADC ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0xFE
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_adc_bcd_off_indexed_indirect_carry_clear_in_carry_set_out(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x71, 0x10) #=> $0000 ADC ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0xFF
    cpu.step()    
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)        
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_adc_bcd_off_indexed_indirect_indexed_overflow(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x61, 0x10) #=> $0000 ADC ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)    
    self.assertEquals(cpu.OVERFLOW, cpu.flags & cpu.OVERFLOW)       
    self.assertEquals(0, cpu.flags & cpu.ZERO)       

  # AND (Absolute)
  
  def test_and_absolute_all_zeros_setting_zero_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0x2D, 0xCD, 0xAB) #=> AND $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_and_absolute_zeros_and_ones_setting_negative_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0x2D, 0xCD, 0xAB) #=> AND $ABCD
    cpu.memory[0xABCD] = 0xAA
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # AND (Absolute)
  
  def test_and_zp_all_zeros_setting_zero_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0001] = (0x25, 0x10) #=> AND $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_and_zp_zeros_and_ones_setting_negative_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0001] = (0x25, 0x10) #=> AND $0010
    cpu.memory[0x0010] = 0xAA
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # AND (Immediate)
  
  def test_and_immediate_all_zeros_setting_zero_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0001] = (0x29, 0x00) #=> AND #$00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_and_immediate_zeros_and_ones_setting_negative_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0001] = (0x29, 0xAA) #=> AND #$AA
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # AND (Absolute, X-Indexed)
  
  def test_and_abs_x_all_zeros_setting_zero_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x3d, 0xCD, 0xAB) #=> AND $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_and_abs_x_zeros_and_ones_setting_negative_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x3d, 0xCD, 0xAB) #=> AND $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0xAA
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # AND (Absolute, Y-Indexed)
  
  def test_and_abs_y_all_zeros_setting_zero_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x39, 0xCD, 0xAB) #=> AND $ABCD,X
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_and_abs_y_zeros_and_ones_setting_negative_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x39, 0xCD, 0xAB) #=> AND $ABCD,X
    cpu.memory[0xABCD + cpu.y] = 0xAA
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  # AND Indirect, Indexed (X)
  
  def test_and_indirect_indexed_x_all_zeros_setting_zero_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x21, 0x10) #=> AND ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_and_indirect_indexed_x_zeros_and_ones_setting_negative_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x21, 0x10) #=> AND ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD    
    cpu.memory[0xABCD] = 0xAA
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  # AND Indexed, Indirect (Y)
  
  def test_and_indexed_indirect_y_all_zeros_setting_zero_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x31, 0x10) #=> AND ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_and_indexed_indirect_y_zeros_and_ones_setting_negative_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x31, 0x10) #=> AND ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0xAA
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  # AND Zero Page, X-Indexed
  
  def test_and_zp_x_all_zeros_setting_zero_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x35, 0x10) #=> AND $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_and_zp_x_all_zeros_and_ones_setting_negative_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x35, 0x10) #=> AND $0010,X
    cpu.memory[0x0010 + cpu.x] = 0xAA
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # ASL Accumulator
  
  def test_asl_accumulator_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.memory[0x0000] = 0x0A #=> ASL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_asl_accumulator_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x40
    cpu.memory[0x0000] = 0x0A #=> ASL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_asl_accumulator_shifts_out_zero(self):
    cpu = MPU()
    cpu.a = 0x7F
    cpu.memory[0x0000] = 0x0A #=> ASL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)

  def test_asl_accumulator_shifts_out_one(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000] = 0x0A #=> ASL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ASL Absolute

  def test_asl_absolute_sets_z_flag(self):
    cpu = MPU()
    cpu.memory[0x0000:0x0002] = (0x0E, 0xCD, 0xAB) #=> ASL $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_asl_absolute_sets_n_flag(self):
    cpu = MPU()
    cpu.memory[0x0000:0x0002] = (0x0E, 0xCD, 0xAB) #=> ASL $ABCD
    cpu.memory[0xABCD] = 0x40
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.memory[0xABCD])
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_asl_absolute_shifts_out_zero(self):
    cpu = MPU()
    cpu.a = 0xAA
    cpu.memory[0x0000:0x0002] = (0x0E, 0xCD, 0xAB) #=> ASL $ABCD
    cpu.memory[0xABCD] = 0x7F
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(0xFE, cpu.memory[0xABCD])
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_asl_absolute_shifts_out_one(self):
    cpu = MPU()
    cpu.a = 0xAA
    cpu.memory[0x0000:0x0002] = (0x0E, 0xCD, 0xAB) #=> ASL $ABCD
    cpu.memory[0xABCD] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(0xFE, cpu.memory[0xABCD])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)
    
  # ASL Zero Page
  
  def test_asl_zp_sets_z_flag(self):
    cpu = MPU()
    cpu.memory[0x0000:0x0001] = (0x06, 0x10) #=> ASL $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_asl_zp_sets_n_flag(self):
    cpu = MPU()
    cpu.memory[0x0000:0x0001] = (0x06, 0x10) #=> ASL $0010
    cpu.memory[0x0010] = 0x40
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.memory[0x0010])
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_asl_zp_shifts_out_zero(self):
    cpu = MPU()
    cpu.a = 0xAA
    cpu.memory[0x0000:0x0001] = (0x06, 0x10) #=> ASL $0010
    cpu.memory[0x0010] = 0x7F
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(0xFE, cpu.memory[0x0010])
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_asl_zp_shifts_out_one(self):
    cpu = MPU()
    cpu.a = 0xAA
    cpu.memory[0x0000:0x0001] = (0x06, 0x10) #=> ASL $0010
    cpu.memory[0x0010] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(0xFE, cpu.memory[0x0010])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ASL Absolute, X-Indexed

  def test_asl_absolute_x_indexed_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x1E, 0xCD, 0xAB) #=> ASL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_asl_absolute_x_indexed_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x1E, 0xCD, 0xAB) #=> ASL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x40
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_asl_absolute_x_indexed_shifts_out_zero(self):
    cpu = MPU()
    cpu.a = 0xAA
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x1E, 0xCD, 0xAB) #=> ASL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x7F
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(0xFE, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_asl_absolute_x_indexed_shifts_out_one(self):
    cpu = MPU()
    cpu.a = 0xAA
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x1E, 0xCD, 0xAB) #=> ASL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(0xFE, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ASL Zero Page, X-Indexed
  
  def test_asl_zp_x_indexed_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x16, 0x10) #=> ASL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_asl_zp_x_indexed_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x16, 0x10) #=> ASL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x40
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_asl_zp_x_indexed_shifts_out_zero(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.a = 0xAA
    cpu.memory[0x0000:0x0001] = (0x16, 0x10) #=> ASL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x7F
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(0xFE, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_asl_zp_x_indexed_shifts_out_one(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.a = 0xAA
    cpu.memory[0x0000:0x0001] = (0x16, 0x10) #=> ASL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xAA, cpu.a)
    self.assertEquals(0xFE, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # BCC
  
  def test_bcc_carry_clear_branches_relative_forward(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0001] = (0x90, 0x06) #=> BCC +6
    cpu.step()
    self.assertEquals(0x0002 + 0x06, cpu.pc)

  def test_bcc_carry_clear_branches_relative_backward(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.pc = 0x0050
    rel = (0x06^0xFF + 1) # two's complement of 6
    cpu.memory[0x0050:0x0051] = (0x90, rel) #=> BCC -6
    cpu.step()
    self.assertEquals(0x0052 + rel, cpu.pc)
  
  def test_bcc_carry_set_does_not_branch(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x90, 0x06) #=> BCC +6
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)

  # BCS
  
  def test_bcs_carry_set_branches_relative_forward(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0xB0, 0x06) #=> BCS +6
    cpu.step()
    self.assertEquals(0x0002 + 0x06, cpu.pc)

  def test_bcs_carry_set_branches_relative_backward(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.pc = 0x0050
    rel = (0x06^0xFF + 1) # two's complement of 6
    cpu.memory[0x0050:0x0051] = (0xB0, rel) #=> BCS -6
    cpu.step()
    self.assertEquals(0x0052 + rel, cpu.pc)
  
  def test_bcs_carry_clear_does_not_branch(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0001] = (0xB0, 0x06) #=> BCS +6
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
  
  # BEQ
  
  def test_beq_zero_set_branches_relative_forward(self):
    cpu = MPU()
    cpu.flags |= cpu.ZERO
    cpu.memory[0x0000:0x0001] = (0xF0, 0x06) #=> BEQ +6
    cpu.step()
    self.assertEquals(0x0002 + 0x06, cpu.pc)
    
  def test_beq_zero_set_branches_relative_backward(self):
    cpu = MPU()
    cpu.flags |= cpu.ZERO
    cpu.pc = 0x0050
    rel = (0x06^0xFF + 1) # two's complement of 6
    cpu.memory[0x0050:0x0051] = (0xF0, rel) #=> BEQ -6
    cpu.step()
    self.assertEquals(0x0052 + rel, cpu.pc)
  
  def test_beq_zero_clear_does_not_branch(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.memory[0x0000:0x0001] = (0xF0, 0x06) #=> BEQ +6
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
  
  # BMI
  
  def test_bmi_negative_set_branches_relative_forward(self):
    cpu = MPU()
    cpu.flags |= cpu.NEGATIVE
    cpu.memory[0x0000:0x0001] = (0x30, 0x06) #=> BMI +06
    cpu.step()
    self.assertEquals(0x0002 + 0x06, cpu.pc)

  def test_bmi_negative_set_branches_relative_backward(self):
    cpu = MPU()
    cpu.flags |= cpu.NEGATIVE
    cpu.pc = 0x0050
    rel = (0x06^0xFF + 1) # two's complement of 6
    cpu.memory[0x0050:0x0051] = (0x30, rel) #=> BMI -6
    cpu.step()
    self.assertEquals(0x0052 + rel, cpu.pc)
        
  def test_bmi_negative_clear_does_not_branch(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.memory[0x0000:0x0001] = (0x30, 0x06) #=> BEQ +6
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    
  # BNE
  
  def test_bne_zero_clear_branches_relative_forward(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.memory[0x0000:0x0001] = (0xD0, 0x06) #=> BNE +6
    cpu.step()
    self.assertEquals(0x0002 + 0x06, cpu.pc)
    
  def test_bne_zero_clear_branches_relative_backward(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.pc = 0x0050
    rel = (0x06^0xFF + 1) # two's complement of 6
    cpu.memory[0x0050:0x0051] = (0xD0, rel) #=> BNE -6
    cpu.step()
    self.assertEquals(0x0052 + rel, cpu.pc)

  def test_bne_zero_set_does_not_branch(self):
    cpu = MPU()
    cpu.flags |= cpu.ZERO
    cpu.memory[0x0000:0x0001] = (0xD0, 0x06) #=> BNE +6
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
  
  # BPL
  
  def test_bpl_negative_clear_branches_relative_forward(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.memory[0x0000:0x0001] = (0x10, 0x06) #=> BPL +06
    cpu.step()
    self.assertEquals(0x0002 + 0x06, cpu.pc)

  def test_bpl_negative_clear_branches_relative_backward(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.pc = 0x0050
    rel = (0x06^0xFF + 1) # two's complement of 6
    cpu.memory[0x0050:0x0051] = (0x10, rel) #=> BPL -6
    cpu.step()
    self.assertEquals(0x0052 + rel, cpu.pc)
        
  def test_bpl_negative_set_does_not_branch(self):
    cpu = MPU()
    cpu.flags |= cpu.NEGATIVE
    cpu.memory[0x0000:0x0001] = (0x10, 0x06) #=> BPL +6
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
  
  # BRK
  
  def test_brk_pushes_pc_plus_2_and_status_then_sets_pc_to_irq_vector(self):
    cpu = MPU()
    cpu.flags = 0x00
    cpu.memory[0xFFFE:0xFFFF] = (0xCD, 0xAB)
    cpu.memory[0xC000]        = 0x00 #=> BRK
    cpu.pc = 0xC000
    cpu.step()
    self.assertEquals(0xABCD, cpu.pc)

    self.assertEquals(0xC0,      cpu.memory[0x1FF]) # PCH
    self.assertEquals(0x03,      cpu.memory[0x1FE]) # PCL
    self.assertEquals(cpu.BREAK, cpu.memory[0x1FD]) # Status (P)
    self.assertEquals(0xFC,      cpu.sp)

    self.assertEquals(cpu.BREAK | cpu.INTERRUPT, cpu.flags)

  # BVC
  
  def test_bvc_overflow_clear_branches_relative_forward(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.OVERFLOW)
    cpu.memory[0x0000:0x0001] = (0x50, 0x06) #=> BVC +6
    cpu.step()
    self.assertEquals(0x0002 + 0x06, cpu.pc)

  def test_bvc_overflow_clear_branches_relative_backward(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.OVERFLOW)
    cpu.pc = 0x0050
    rel = (0x06^0xFF + 1) # two's complement of 6
    cpu.memory[0x0050:0x0051] = (0x50, rel) #=> BVC -6
    cpu.step()
    self.assertEquals(0x0052 + rel, cpu.pc)
  
  def test_bvc_overflow_set_does_not_branch(self):
    cpu = MPU()
    cpu.flags |= cpu.OVERFLOW
    cpu.memory[0x0000:0x0001] = (0x50, 0x06) #=> BVC +6
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)

  # BVS
  
  def test_bvs_overflow_set_branches_relative_forward(self):
    cpu = MPU()
    cpu.flags |= cpu.OVERFLOW
    cpu.memory[0x0000:0x0001] = (0x70, 0x06) #=> BVS +6
    cpu.step()
    self.assertEquals(0x0002 + 0x06, cpu.pc)

  def test_bvs_overflow_set_branches_relative_backward(self):
    cpu = MPU()
    cpu.flags |= cpu.OVERFLOW
    cpu.pc = 0x0050
    rel = (0x06^0xFF + 1) # two's complement of 6
    cpu.memory[0x0050:0x0051] = (0x70, rel) #=> BVS -6
    cpu.step()
    self.assertEquals(0x0052 + rel, cpu.pc)
  
  def test_bvs_overflow_clear_does_not_branch(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.OVERFLOW)
    cpu.memory[0x0000:0x0001] = (0x70, 0x06) #=> BVS +6
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)

  # CLC
  
  def test_clc_clears_carry_flag(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000] = 0x18 #=> CLC
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
      
  # CLD
  
  def test_cld_clears_decimal_flag(self):
    cpu = MPU()
    cpu.flags |= cpu.DECIMAL
    cpu.memory[0x0000] = 0xD8 #=> CLD
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0, cpu.flags & cpu.DECIMAL)
    
  # CLI
  
  def test_cli_clears_interrupt_mask_flag(self):
    cpu = MPU()
    cpu.flags |= cpu.INTERRUPT
    cpu.memory[0x0000] = 0x58 #=> CLI
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0, cpu.flags & cpu.INTERRUPT)
      
  # CLV
  
  def test_clv_clears_overflow_flag(self):
    cpu = MPU()
    cpu.flags |= cpu.OVERFLOW
    cpu.memory[0x0000] = 0xB8 #=> CLV
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0, cpu.flags & cpu.OVERFLOW)
        
  # DEX
  
  def test_dex_decrements_x(self):
    cpu = MPU()
    cpu.x = 0x10
    cpu.memory[0x0000] = 0xCA #=> DEX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x0F, cpu.x)
      
  def test_dex_below_00_rolls_over_and_sets_negative_flag(self):
    cpu = MPU()
    cpu.x = 0x00
    cpu.memory[0x0000] = 0xCA #=> DEX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xFF, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    
  def test_dex_sets_zero_flag_when_decrementing_to_zero(self):
    cpu = MPU()
    cpu.x = 0x01
    cpu.memory[0x0000] = 0xCA #=> DEX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    
  # DEY
  
  def test_dey_decrements_y(self):
    cpu = MPU()
    cpu.y = 0x10
    cpu.memory[0x0000] = 0x88 #=> DEY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x0F, cpu.y)
      
  def test_dey_below_00_rolls_over_and_sets_negative_flag(self):
    cpu = MPU()
    cpu.y = 0x00
    cpu.memory[0x0000] = 0x88 #=> DEY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xFF, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    
  def test_dey_sets_zero_flag_when_decrementing_to_zero(self):
    cpu = MPU()
    cpu.y = 0x01
    cpu.memory[0x0000] = 0x88 #=> DEY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    
  # INX

  def test_inx_increments_x(self):
    cpu = MPU()
    cpu.x = 0x09
    cpu.memory[0x0000] = 0xE8 #=> INX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x0A, cpu.x)
    
  def test_inx_above_FF_rolls_over_and_sets_zero_flag(self):
    cpu = MPU()
    cpu.x = 0xFF
    cpu.memory[0x0000] = 0xE8 #=> INX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    
  def test_inx_sets_negative_flag_when_incrementing_above_7F(self):
    cpu = MPU()
    cpu.x = 0x7f
    cpu.memory[0x0000] = 0xE8 #=> INX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    
  # INY

  def test_iny_increments_y(self):
    cpu = MPU()
    cpu.y = 0x09
    cpu.memory[0x0000] = 0xC8 #=> INY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x0A, cpu.y)
    
  def test_iny_above_FF_rolls_over_and_sets_zero_flag(self):
    cpu = MPU()
    cpu.y = 0xFF
    cpu.memory[0x0000] = 0xC8 #=> INY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    
  def test_iny_sets_negative_flag_when_incrementing_above_7F(self):
    cpu = MPU()
    cpu.y = 0x7f
    cpu.memory[0x0000] = 0xC8 #=> INY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    
  # JMP
  
  def test_jmp_jumps_to_absolute_address(self):
    cpu = MPU()
    cpu.memory[0x0000:0x0002] = (0x4C, 0xCD, 0xAB) #=> JMP $ABCD
    cpu.step()
    self.assertEquals(0xABCD, cpu.pc)
  
  def test_jmp_jumps_to_indirect_address(self):
    cpu = MPU()
    cpu.memory[0x0000:0x0002] = (0x6C, 0x00, 0x02) #=> JMP ($ABCD)
    cpu.memory[0x0200:0x0201] = (0xCD, 0xAB)
    cpu.step()
    self.assertEquals(0xABCD, cpu.pc)

  # JSR
  
  def test_jsr_pushes_pc_plus_2_and_sets_pc(self):
    cpu = MPU()
    cpu.memory[0xC000:0xC002] = (0x20, 0xD2, 0xFF) #=> JSR $FFD2
    cpu.pc = 0xC000
    cpu.step()
    self.assertEquals(0xFFD2, cpu.pc)
    self.assertEquals(0xFD,   cpu.sp)
    self.assertEquals(0xC0,   cpu.memory[0x01FF]) # PCH
    self.assertEquals(0x02,   cpu.memory[0x01FE]) # PCL+2

  # LDA Absolute
  
  def test_lda_absolute_loads_a_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.memory[0x0000:0x0002] = (0xAD, 0xCD, 0xAB) #=> LDA $ABCD
    cpu.memory[0xABCD] = 0x80
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_lda_absolute_loads_a_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0xAD, 0xCD, 0xAB) #=> LDA $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDA Absolute
  
  def test_lda_absolute_loads_a_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.memory[0x0000:0x0002] = (0xAD, 0xCD, 0xAB) #=> LDA $ABCD
    cpu.memory[0xABCD] = 0x80
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_lda_absolute_loads_a_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0xAD, 0xCD, 0xAB) #=> LDA $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDA Zero Page

  def test_lda_zp_loads_a_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.memory[0x0000:0x0002] = (0xA5, 0x10) #=> LDA $0010
    cpu.memory[0x0010] = 0x80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_lda_zp_loads_a_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0xA5, 0x10) #=> LDA $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDA Immediate
  
  def test_lda_immediate_loads_a_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.memory[0x0000:0x0002] = (0xA9, 0x80) #=> LDA #$80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_ldx_immediate_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0xA2, 0x00) #=> LDA #$00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDA Absolute, X-Indexed
  
  def test_lda_absolute_x_indexed_loads_a_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0xBD, 0xCD, 0xAB) #=> LDA $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x80
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_lda_absolute_x_indexed_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0xBD, 0xCD, 0xAB) #=> LDA $ABCD,X
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDA Absolute, Y-Indexed
  
  def test_lda_absolute_y_indexed_loads_a_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0xB9, 0xCD, 0xAB) #=> LDA $ABCD,Y
    cpu.memory[0xABCD + cpu.y] = 0x80
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_lda_absolute_y_indexed_loads_a_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0xB9, 0xCD, 0xAB) #=> LDA $ABCD,Y
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDA Indirect, Indexed (X)
  
  def test_lda_indirect_indexed_x_loads_a_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0xA1, 0x10) #=> LDA ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0x80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_lda_indirect_indexed_x_loads_a_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0xA1, 0x10) #=> LDA ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDA Indexed, Indirect (Y)
  
  def test_lda_indexed_indirect_y_loads_a_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0xB1, 0x10) #=> LDA ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0x80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_lda_indexed_indirect_y_loads_a_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0xB1, 0x10) #=> LDA ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDA Zero Page, X-Indexed

  def test_lda_zp_x_indexed_loads_x_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0xB5, 0x10) #=> LDA $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_lda_zp_x_indexed_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0xB5, 0x10) #=> LDA $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)  

  # LDX Absolute
  
  def test_ldx_absolute_loads_x_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x00
    cpu.memory[0x0000:0x0002] = (0xAE, 0xCD, 0xAB) #=> LDX $ABCD
    cpu.memory[0xABCD] = 0x80
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_ldx_absolute_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0xFF
    cpu.memory[0x0000:0x0002] = (0xAE, 0xCD, 0xAB) #=> LDX $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDX Zero Page

  def test_ldx_zp_loads_x_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x00
    cpu.memory[0x0000:0x0002] = (0xA6, 0x10) #=> LDX $0010
    cpu.memory[0x0010] = 0x80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_ldx_zp_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0xFF
    cpu.memory[0x0000:0x0002] = (0xA6, 0x10) #=> LDX $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDX Immediate

  def test_ldx_immediate_loads_x_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x00
    cpu.memory[0x0000:0x0002] = (0xA2, 0x80) #=> LDX #$80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_ldx_immediate_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0xFF
    cpu.memory[0x0000:0x0002] = (0xA2, 0x00) #=> LDX #$00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDX Absolute, Y-Indexed
  
  def test_ldx_absolute_y_indexed_loads_x_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0xBE, 0xCD, 0xAB) #=> LDX $ABCD,Y
    cpu.memory[0xABCD + cpu.y] = 0x80
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_ldx_absolute_y_indexed_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0xBE, 0xCD, 0xAB) #=> LDX $ABCD,Y
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDX Zero Page, Y-Indexed

  def test_ldx_zp_y_indexed_loads_x_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0xB6, 0x10) #=> LDX $0010,Y
    cpu.memory[0x0010 + cpu.y] = 0x80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_ldx_zp_y_indexed_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0xB6, 0x10) #=> LDX $0010,Y
    cpu.memory[0x0010 + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDY Absolute
  
  def test_ldy_absolute_loads_y_sets_n_flag(self):
    cpu = MPU()
    cpu.y = 0x00
    cpu.memory[0x0000:0x0002] = (0xAC, 0xCD, 0xAB) #=> LDY $ABCD
    cpu.memory[0xABCD] = 0x80
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_ldy_absolute_loads_y_sets_z_flag(self):
    cpu = MPU()
    cpu.y = 0xFF
    cpu.memory[0x0000:0x0002] = (0xAC, 0xCD, 0xAB) #=> LDY $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
  
  # LDY Zero Page
  
  def test_ldy_zp_loads_y_sets_n_flag(self):
    cpu = MPU()
    cpu.y = 0x00
    cpu.memory[0x0000:0x0002] = (0xA4, 0x10) #=> LDY $0010
    cpu.memory[0x0010] = 0x80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  def test_ldy_zp_loads_y_sets_z_flag(self):
    cpu = MPU()
    cpu.y = 0xFF
    cpu.memory[0x0000:0x0002] = (0xA4, 0x10) #=> LDY $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
  
  # LDY Immediate
  
  def test_ldy_immediate_loads_y_sets_n_flag(self):
    cpu = MPU()
    cpu.y = 0x00
    cpu.memory[0x0000:0x0002] = (0xA0, 0x80) #=> LDY #$80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_ldy_immediate_loads_y_sets_z_flag(self):
    cpu = MPU()
    cpu.y = 0xFF
    cpu.memory[0x0000:0x0002] = (0xA0, 0x00) #=> LDY #$00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LDY Absolute, X-Indexed
  
  def test_ldy_absolute_x_indexed_loads_x_sets_n_flag(self):
    cpu = MPU()
    cpu.y = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0xBC, 0xCD, 0xAB) #=> LDY $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x80
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_ldy_absolute_x_indexed_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.y = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0xBC, 0xCD, 0xAB) #=> LDY $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
  
  # LDY Zero Page, X-Indexed
  
  def test_ldy_zp_x_indexed_loads_x_sets_n_flag(self):
    cpu = MPU()
    cpu.y = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0xB4, 0x10) #=> LDY $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x80
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_ldy_zp_x_indexed_loads_x_sets_z_flag(self):
    cpu = MPU()
    cpu.y = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0xB4, 0x10) #=> LDY $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  # LSR Accumulator

  def test_lsr_accumulator_rotates_in_zero_not_carry(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000] = (0x4A) #=> LSR A
    mpu.a = 0x00
    mpu.step()
    self.assertEquals(0x0001, mpu.pc)
    self.assertEquals(0x00, mpu.a)
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)

  def test_lsr_accumulator_sets_carry_and_zero_flags_after_rotation(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000] = (0x4A) #=> LSR A
    mpu.a = 0x01
    mpu.step()
    self.assertEquals(0x0001, mpu.pc) 
    self.assertEquals(0x00, mpu.a)
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(mpu.CARRY, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)
    
  def test_lsr_accumulator_rotates_bits_right(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000] = (0x4A) #=> LSR A
    mpu.a = 0x04
    mpu.step()    
    self.assertEquals(0x0001, mpu.pc)   
    self.assertEquals(0x02, mpu.a)
    self.assertEquals(0, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)    

  # LSR Absolute

  def test_lsr_absolute_rotates_in_zero_not_carry(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000:0x0002] = (0x4E, 0xCD, 0xAB) #=> LSR $ABCD
    mpu.memory[0xABCD] = 0x00
    mpu.step()
    self.assertEquals(0x0003, mpu.pc)
    self.assertEquals(0x00, mpu.memory[0xABCD])
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)

  def test_lsr_absolute_sets_carry_and_zero_flags_after_rotation(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000:0x0002] = (0x4E, 0xCD, 0xAB) #=> LSR $ABCD
    mpu.memory[0xABCD] = 0x01
    mpu.step()
    self.assertEquals(0x0003, mpu.pc)    
    self.assertEquals(0x00, mpu.memory[0xABCD])
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(mpu.CARRY, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)
    
  def test_lsr_absolute_rotates_bits_right(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000:0x0002] = (0x4E, 0xCD, 0xAB) #=> LSR $ABCD
    mpu.memory[0xABCD] = 0x04
    mpu.step()    
    self.assertEquals(0x0003, mpu.pc)    
    self.assertEquals(0x02, mpu.memory[0xABCD])
    self.assertEquals(0, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)    

  # LSR Zero Page

  def test_lsr_zp_rotates_in_zero_not_carry(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000:0x0001] = (0x46, 0x10) #=> LSR $0010
    mpu.memory[0x0010] = 0x00
    mpu.step()
    self.assertEquals(0x0002, mpu.pc)
    self.assertEquals(0x00, mpu.memory[0x0010])
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)

  def test_lsr_zp_sets_carry_and_zero_flags_after_rotation(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000:0x0001] = (0x46, 0x10) #=> LSR $0010
    mpu.memory[0x0010] = 0x01
    mpu.step()
    self.assertEquals(0x0002, mpu.pc)    
    self.assertEquals(0x00, mpu.memory[0x0010])
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(mpu.CARRY, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)
    
  def test_lsr_zp_rotates_bits_right(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000:0x0001] = (0x46, 0x10) #=> LSR $0010
    mpu.memory[0x0010] = 0x04
    mpu.step()    
    self.assertEquals(0x0002, mpu.pc)    
    self.assertEquals(0x02, mpu.memory[0x0010])
    self.assertEquals(0, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)    
  
  # LSR Absolute, X-Indexed

  def test_lsr_absolute_x_indexed_rotates_in_zero_not_carry(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.x = 0x03
    mpu.memory[0x0000:0x0002] = (0x5E, 0xCD, 0xAB) #=> LSR $ABCD,X
    mpu.memory[0xABCD + mpu.x] = 0x00
    mpu.step()
    self.assertEquals(0x0003, mpu.pc)
    self.assertEquals(0x00, mpu.memory[0xABCD + mpu.x])
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)

  def test_lsr_absolute_x_indexed_sets_carry_and_zero_flags_after_rotation(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.x = 0x03
    mpu.memory[0x0000:0x0002] = (0x5E, 0xCD, 0xAB) #=> LSR $ABCD,X
    mpu.memory[0xABCD + mpu.x] = 0x01
    mpu.step()
    self.assertEquals(0x0003, mpu.pc)    
    self.assertEquals(0x00, mpu.memory[0xABCD + mpu.x])
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(mpu.CARRY, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)
    
  def test_lsr_absolute_x_indexed_rotates_bits_right(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.memory[0x0000:0x0002] = (0x5E, 0xCD, 0xAB) #=> LSR $ABCD,X
    mpu.memory[0xABCD + mpu.x] = 0x04
    mpu.step()    
    self.assertEquals(0x0003, mpu.pc)    
    self.assertEquals(0x02, mpu.memory[0xABCD + mpu.x])
    self.assertEquals(0, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)    

  # LSR Zero Page, X-Indexed

  def test_lsr_zp_x_indexed_rotates_in_zero_not_carry(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.x = 0x03
    mpu.memory[0x0000:0x0001] = (0x56, 0x10) #=> LSR $0010,X
    mpu.memory[0x0010 + mpu.x] = 0x00
    mpu.step()
    self.assertEquals(0x0002, mpu.pc)
    self.assertEquals(0x00, mpu.memory[0x0010 + mpu.x])
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)

  def test_lsr_zp_x_indexed_sets_carry_and_zero_flags_after_rotation(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.x = 0x03
    mpu.memory[0x0000:0x0001] = (0x56, 0x10) #=> LSR $0010,X
    mpu.memory[0x0010 + mpu.x] = 0x01
    mpu.step()
    self.assertEquals(0x0002, mpu.pc)    
    self.assertEquals(0x00, mpu.memory[0x0010 + mpu.x])
    self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
    self.assertEquals(mpu.CARRY, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)
    
  def test_lsr_zp_x_indexed_rotates_bits_right(self):
    mpu = MPU()
    mpu.flags &= mpu.CARRY
    mpu.x = 0x03
    mpu.memory[0x0000:0x0001] = (0x56, 0x10) #=> LSR $0010,X
    mpu.memory[0x0010 + mpu.x] = 0x04
    mpu.step()    
    self.assertEquals(0x0002, mpu.pc)    
    self.assertEquals(0x02, mpu.memory[0x0010 + mpu.x])
    self.assertEquals(0, mpu.flags & mpu.ZERO)
    self.assertEquals(0, mpu.flags & mpu.CARRY)
    self.assertEquals(0, mpu.flags & mpu.NEGATIVE)    

  # NOP
  
  def test_nop_does_nothing(self):
    cpu = MPU()
    cpu.memory[0x0000] = 0xEA #=> NOP
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)

  # ORA Absolute
  
  def test_ora_absolute_zeroes_or_zeros_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.memory[0x0000:0x0001] = (0x0D, 0xCD, 0xAB) #=> ORA $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_ora_absolute_turns_bits_on_sets_n_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x03
    cpu.memory[0x0000:0x0001] = (0x0D, 0xCD, 0xAB) #=> ORA $ABCD
    cpu.memory[0xABCD] = 0x82
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x83, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # ORA Zero Page
  
  def test_ora_zp_zeroes_or_zeros_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.memory[0x0000:0x0001] = (0x05, 0x10) #=> ORA $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_ora_zp_turns_bits_on_sets_n_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x03
    cpu.memory[0x0000:0x0001] = (0x05, 0x10) #=> ORA $0010
    cpu.memory[0x0010] = 0x82
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x83, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # ORA Immediate
  
  def test_ora_immediate_zeroes_or_zeros_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.memory[0x0000:0x0001] = (0x09, 0x00) #=> ORA #$00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
  
  def test_ora_immediate_turns_bits_on_sets_n_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x03
    cpu.memory[0x0000:0x0001] = (0x09, 0x82) #=> ORA #$82
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x83, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # ORA Absolute, X
  
  def test_ora_absolute_x_indexed_zeroes_or_zeros_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x1D, 0xCD, 0xAB) #=> ORA $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_ora_absolute_x_indexed_turns_bits_on_sets_n_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x03
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x1D, 0xCD, 0xAB) #=> ORA $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x82
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x83, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # ORA Absolute, Y
  
  def test_ora_absolute_y_indexed_zeroes_or_zeros_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x19, 0xCD, 0xAB) #=> ORA $ABCD,Y
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_ora_absolute_y_indexed_turns_bits_on_sets_n_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x03
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x19, 0xCD, 0xAB) #=> ORA $ABCD,Y
    cpu.memory[0xABCD + cpu.y] = 0x82
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x83, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # ORA Indirect, Indexed (X)
  
  def test_ora_indirect_indexed_x_zeroes_or_zeros_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x01, 0x10) #=> ORA ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_ora_indirect_indexed_x_turns_bits_on_sets_n_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x03
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x01, 0x10) #=> ORA ($ABCD,X)
    cpu.memory[0x0013:0x0014] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD] = 0x82
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x83, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # ORA Indexed, Indirect (Y)
  
  def test_ora_indexed_indirect_y_zeroes_or_zeros_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x11, 0x10) #=> ORA ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_ora_indexed_indirect_y_turns_bits_on_sets_n_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x03
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x11, 0x10) #=> ORA ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xCD, 0xAB) #=> Vector to $ABCD
    cpu.memory[0xABCD + cpu.y] = 0x82
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x83, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # ORA Zero Page, X
  
  def test_ora_zp_x_indexed_zeroes_or_zeros_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x15, 0x10) #=> ORA $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  def test_ora_zp_x_indexed_turns_bits_on_sets_n_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x03
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x15, 0x10) #=> ORA $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x82
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x83, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # PHA
  
  def test_pha_pushes_a_and_updates_sp(self):
    cpu = MPU()
    cpu.a = 0xAB
    cpu.memory[0x0000] = 0x48 #=> PHA
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB, cpu.a)
    self.assertEquals(0xAB, cpu.memory[0x01FF])
    self.assertEquals(0xFE, cpu.sp)
    
  # PHP
  
  def test_php_pushes_processor_status_and_updates_sp(self):
    cpu = MPU()
    flags = (cpu.NEGATIVE | cpu.OVERFLOW | cpu.DECIMAL | cpu.ZERO | cpu.CARRY)
    cpu.flags = flags
    cpu.memory[0x0000] = 0x08 #=> PHP
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(flags,  cpu.memory[0x1FF])
    self.assertEquals(0xFE,   cpu.sp)

  # PLA
  
  def test_pla_pulls_top_byte_from_stack_into_a_and_updates_sp(self):
    cpu = MPU()
    cpu.memory[0x0000] = 0x68 #=> PLA
    cpu.memory[0x01FF] = 0xAB
    cpu.sp = 0xFE
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB,   cpu.a)
    self.assertEquals(0xFF,   cpu.sp)

  # PLP
  
  def test_plp_pulls_top_byte_from_stack_into_flags_and_updates_sp(self):
    cpu = MPU()
    cpu.memory[0x0000] = 0x28 #=> PLP
    cpu.memory[0x01FF] = 0xAB
    cpu.sp = 0xFE
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB,   cpu.flags)
    self.assertEquals(0xFF,   cpu.sp)

  # ROL Accumulator
  
  def test_rol_accumulator_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000] = 0x2A #=> ROL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_rol_accumulator_zero_and_carry_one_clears_z_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000] = 0x2A #=> ROL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x01, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
  
  def test_rol_accumulator_sets_n_flag(self):
    cpu = MPU()
    cpu.a = 0x40
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000] = 0x2A #=> ROL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x81, cpu.a)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_rol_accumulator_shifts_out_zero(self):
    cpu = MPU()
    cpu.a = 0x7F
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000] = 0x0A #=> ROL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_rol_accumulator_shifts_out_one(self):
    cpu = MPU()
    cpu.a = 0xFF
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000] = 0x2A #=> ROL A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xFE, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROL Absolute
  
  def test_rol_absolute_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0002] = (0x2E, 0xCD, 0xAB) #=> ROL $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_rol_absolute_zero_and_carry_one_clears_z_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x2E, 0xCD, 0xAB) #=> ROL $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x01, cpu.memory[0xABCD])
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
  
  def test_rol_absolute_sets_n_flag(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x2E, 0xCD, 0xAB) #=> ROL $ABCD
    cpu.memory[0xABCD] = 0x40    
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0xABCD])
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_rol_absolute_shifts_out_zero(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0002] = (0x2E, 0xCD, 0xAB) #=> ROL $ABCD
    cpu.memory[0xABCD] = 0x7F    
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFE, cpu.memory[0xABCD])
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_rol_absolute_shifts_out_one(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0002] = (0x2E, 0xCD, 0xAB) #=> ROL $ABCD
    cpu.memory[0xABCD] = 0xFF    
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFE, cpu.memory[0xABCD])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROL Zero Page
  
  def test_rol_zp_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0001] = (0x26, 0x10) #=> ROL $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_rol_zp_zero_and_carry_one_clears_z_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x26, 0x10) #=> ROL $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.memory[0x0010])
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
  
  def test_rol_zp_sets_n_flag(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x26, 0x10) #=> ROL $0010
    cpu.memory[0x0010] = 0x40    
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0x0010])
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_rol_zp_shifts_out_zero(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0001] = (0x26, 0x10) #=> ROL $0010
    cpu.memory[0x0010] = 0x7F    
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.memory[0x0010])
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_rol_zp_shifts_out_one(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0001] = (0x26, 0x10) #=> ROL $0010
    cpu.memory[0x0010] = 0xFF    
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.memory[0x0010])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROL Absolute, X-Indexed
  
  def test_rol_absolute_x_indexed_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x3E, 0xCD, 0xAB) #=> ROL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_rol_absolute_x_indexed_zero_and_carry_one_clears_z_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x3E, 0xCD, 0xAB) #=> ROL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x01, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
  
  def test_rol_absolute_x_indexed_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x3E, 0xCD, 0xAB) #=> ROL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x40    
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_rol_absolute_x_indexed_shifts_out_zero(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0002] = (0x3E, 0xCD, 0xAB) #=> ROL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x7F    
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFE, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_rol_absolute_x_indexed_shifts_out_one(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0002] = (0x3E, 0xCD, 0xAB) #=> ROL $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0xFF    
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFE, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROL Zero Page, X-Indexed
  
  def test_rol_zp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x36, 0x10) #=> ROL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_rol_zp_x_indexed_zero_and_carry_one_clears_z_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x36, 0x10) #=> ROL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x01, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
  
  def test_rol_zp_x_indexed_sets_n_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x36, 0x10) #=> ROL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x40    
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
  
  def test_rol_zp_x_indexed_shifts_out_zero(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0001] = (0x36, 0x10) #=> ROL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x7F    
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.CARRY)
  
  def test_rol_zp_x_indexed_shifts_out_one(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000:0x0001] = (0x36, 0x10) #=> ROL $0010,X
    cpu.memory[0x0010 + cpu.x] = 0xFF    
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFE, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROR Accumulator

  def test_ror_accumulator_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.flags &= ~(cpu.CARRY)    
    cpu.memory[0x0000] = 0x6A #=> ROR A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    
  def test_ror_accumulator_zero_and_carry_one_rotates_in_sets_n_flags(self):
    cpu = MPU()
    cpu.a = 0x00
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000] = 0x6A #=> ROR A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)

  def test_ror_accumulator_shifts_out_zero(self):
    cpu = MPU()
    cpu.a = 0x02
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000] = 0x6A #=> ROR A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x81, cpu.a)
    self.assertEquals(0, cpu.flags & cpu.CARRY)    

  def test_ror_accumulator_shifts_out_one(self):
    cpu = MPU()
    cpu.a = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000] = 0x6A #=> ROR A
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x81, cpu.a)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROR Absolute

  def test_ror_absolute_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)    
    cpu.memory[0x0000:0x0002] = (0x6E, 0xCD, 0xAB) #=> ROR $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    
  def test_ror_absolute_zero_and_carry_one_rotates_in_sets_n_flags(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x6E, 0xCD, 0xAB) #=> ROR $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.memory[0xABCD])
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
  
  def test_ror_absolute_shifts_out_zero(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x6E, 0xCD, 0xAB) #=> ROR $ABCD
    cpu.memory[0xABCD] = 0x02
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0xABCD])
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
  
  def test_ror_absolute_shifts_out_one(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x6E, 0xCD, 0xAB) #=> ROR $ABCD
    cpu.memory[0xABCD] = 0x03
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0xABCD])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROR Zero Page

  def test_ror_zp_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)    
    cpu.memory[0x0000:0x0001] = (0x66, 0x10) #=> ROR $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_ror_zp_zero_and_carry_one_rotates_in_sets_n_flags(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x66, 0x10) #=> ROR $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.memory[0x0010])
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
  
  def test_ror_zp_zero_absolute_shifts_out_zero(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x66, 0x10) #=> ROR $0010
    cpu.memory[0x0010] = 0x02
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0x0010])
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
  
  def test_ror_zp_shifts_out_one(self):
    cpu = MPU()
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x66, 0x10) #=> ROR $0010
    cpu.memory[0x0010] = 0x03
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0x0010])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROR Absolute, X-Indexed

  def test_ror_absolute_x_indexed_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags &= ~(cpu.CARRY)    
    cpu.memory[0x0000:0x0002] = (0x7E, 0xCD, 0xAB) #=> ROR $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)
    
  def test_ror_absolute_x_indexed_zero_and_carry_one_rotates_in_sets_n_flags(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x7E, 0xCD, 0xAB) #=> ROR $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x80, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
  
  def test_ror_absolute_x_indexed_shifts_out_zero(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x7E, 0xCD, 0xAB) #=> ROR $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x02
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
  
  def test_ror_absolute_x_indexed_shifts_out_one(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0002] = (0x7E, 0xCD, 0xAB) #=> ROR $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x03
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # ROR Zero Page, X-Indexed

  def test_ror_zp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags &= ~(cpu.CARRY)    
    cpu.memory[0x0000:0x0001] = (0x76, 0x10) #=> ROR $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_ror_zp_x_indexed_zero_and_carry_one_rotates_in_sets_n_flags(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x76, 0x10) #=> ROR $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x80, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.ZERO)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
  
  def test_ror_zp_x_indexed_zero_absolute_shifts_out_zero(self):
    cpu = MPU()
    cpu.x = 0x03
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x76, 0x10) #=> ROR $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x02
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0, cpu.flags & cpu.CARRY)    
  
  def test_ror_zp_x_indexed_shifts_out_one(self):
    cpu = MPU()
    cpu.x = 0x03    
    cpu.flags |= cpu.CARRY
    cpu.memory[0x0000:0x0001] = (0x76, 0x10) #=> ROR $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x03
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x81, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)

  # RTI
  
  def test_rti_restores_status_register_and_program_counter_and_updates_sp(self):
    cpu = MPU()
    cpu.memory[0x0000] = 0x40 #=> RTI
    cpu.memory[0x01FD:0x01FF] = (0xAB, 0x03, 0xC0) # Status (P), PCL, PCH
    cpu.sp = 0xFC

    cpu.step()
    self.assertEquals(0xC003, cpu.pc)
    self.assertEquals(0xAB,   cpu.flags)
    self.assertEquals(0xFF,   cpu.sp)

  # RTS
  
  def test_rts_restores_program_counter_and_increments_then_updates_sp(self):
    cpu = MPU()
    cpu.memory[0x0000] = 0x60 #=> RTS
    cpu.memory[0x01FE:0x01FF] = (0x03, 0xC0) # PCL, PCH
    cpu.sp = 0xFD

    cpu.step()
    self.assertEquals(0xC004, cpu.pc)
    self.assertEquals(0xFF,   cpu.sp)

  # SEC
  
  def test_sec_sets_carry_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.CARRY)
    cpu.memory[0x0000] = 0x038 #=> SEC
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(cpu.CARRY, cpu.flags & cpu.CARRY)
    
  # SED
  
  def test_sed_sets_decimal_mode_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.DECIMAL)
    cpu.memory[0x0000] = 0xF8 #=> SED
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(cpu.DECIMAL, cpu.flags & cpu.DECIMAL)
  
  # SEI
  
  def test_sei_sets_interrupt_disable_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.INTERRUPT)
    cpu.memory[0x0000] = 0x78 #=> SEI
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)    
    self.assertEquals(cpu.INTERRUPT, cpu.flags & cpu.INTERRUPT)

  # STA Absolute
  
  def test_sta_absolute_stores_a_leaves_a_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0002] = (0x8D, 0xCD, 0xAB) #=> STA $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0xABCD])
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(flags, cpu.flags)

  def test_sta_absolute_stores_a_leaves_a_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.memory[0x0000:0x0002] = (0x8D, 0xCD, 0xAB) #=> STA $ABCD
    cpu.memory[0xABCD] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD])
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(flags, cpu.flags)

  # STA Zero Page

  def test_sta_zp_stores_a_leaves_a_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.a = 0xFF
    cpu.memory[0x0000:0x0001] = (0x85, 0x10) #=> STA $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0x0010])
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(flags, cpu.flags)

  def test_sta_zp_stores_a_leaves_a_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.memory[0x0000:0x0001] = (0x85, 0x10) #=> STA $0010
    cpu.memory[0x0010] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010])
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(flags, cpu.flags)

  # STA Absolute, X-Indexed
  
  def test_sta_absolute_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x9D, 0xCD, 0xAB) #=> STA $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(flags, cpu.flags)

  def test_sta_absolute_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x9D, 0xCD, 0xAB) #=> STA $ABCD,X
    cpu.memory[0xABCD + cpu.x] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD + cpu.x])
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(flags, cpu.flags)

  # STA Absolute, Y-Indexed
  
  def test_sta_absolute_y_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.a = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x99, 0xCD, 0xAB) #=> STA $ABCD,Y
    cpu.memory[0xABCD + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0xABCD + cpu.y])
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(flags, cpu.flags)

  def test_sta_absolute_y_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0002] = (0x99, 0xCD, 0xAB) #=> STA $ABCD,Y
    cpu.memory[0xABCD + cpu.y] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD + cpu.y])
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(flags, cpu.flags)

  # STA Indirect, Indexed (X)
  
  def test_sta_indirect_indexed_x_stores_a_leaves_a_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x81, 0x10) #=> STA ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xED, 0xFE) #=> Vector to $FEED
    cpu.memory[0xFEED] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0xFEED])
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(flags, cpu.flags)

  def test_sta_indirect_indexed_x_stores_a_leaves_a_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x81, 0x10) #=> STA ($0010,X)
    cpu.memory[0x0013:0x0014] = (0xED, 0xFE) #=> Vector to $FEED
    cpu.memory[0xFEED] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xFEED])
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(flags, cpu.flags)

  # STA Indexed, Indirect (Y)
  
  def test_sta_indexed_indirect_y_stores_a_leaves_a_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.a = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x91, 0x10) #=> STA ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xED, 0xFE) #=> Vector to $FEED
    cpu.memory[0xFEED + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0xFEED + cpu.y])
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(flags, cpu.flags)
    
  def test_sta_indexed_indirect_y_stores_a_leaves_a_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x91, 0x10) #=> STA ($0010),Y
    cpu.memory[0x0010:0x0011] = (0xED, 0xFE) #=> Vector to $FEED
    cpu.memory[0xFEED + cpu.y] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xFEED + cpu.y])
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(flags, cpu.flags)
  
  # STA Zero Page, X-Indexed
  
  def test_sta_zp_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.a = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x95, 0x10) #=> STA $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0xFF, cpu.a)
    self.assertEquals(flags, cpu.flags)

  def test_sta_zp_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0002] = (0x95, 0x10) #=> STA $0010,X
    cpu.memory[0x0010 + cpu.x] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(flags, cpu.flags)

  # STX Absolute
  
  def test_stx_absolute_stores_x_leaves_x_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.x = 0xFF
    cpu.memory[0x0000:0x0002] = (0x8E, 0xCD, 0xAB) #=> STX $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0xABCD])
    self.assertEquals(0xFF, cpu.x)
    self.assertEquals(flags, cpu.flags)

  def test_stx_absolute_stores_x_leaves_x_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.x = 0x00
    cpu.memory[0x0000:0x0002] = (0x8E, 0xCD, 0xAB) #=> STX $ABCD
    cpu.memory[0xABCD] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD])
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(flags, cpu.flags)

  # STX Zero Page

  def test_stx_zp_stores_x_leaves_x_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.x = 0xFF
    cpu.memory[0x0000:0x0001] = (0x86, 0x10) #=> STX $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0x0010])
    self.assertEquals(0xFF, cpu.x)
    self.assertEquals(flags, cpu.flags)

  def test_stx_zp_stores_x_leaves_x_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.x = 0x00
    cpu.memory[0x0000:0x0001] = (0x86, 0x10) #=> STX $0010
    cpu.memory[0x0010] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010])
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(flags, cpu.flags)
 
  # STX Zero Page, Y-Indexed
  
  def test_stx_zp_y_indexed_stores_x_leaves_x_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.x = 0xFF
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x96, 0x10) #=> STX $0010,Y
    cpu.memory[0x0010 + cpu.y] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0x0010 + cpu.y])
    self.assertEquals(0xFF, cpu.x)
    self.assertEquals(flags, cpu.flags)

  def test_stx_zp_y_indexed_stores_x_leaves_x_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.x = 0x00
    cpu.y = 0x03
    cpu.memory[0x0000:0x0001] = (0x96, 0x10) #=> STX $0010,Y
    cpu.memory[0x0010 + cpu.y] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010 + cpu.y])
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(flags, cpu.flags)

  # STY Absolute
  
  def test_sty_absolute_stores_y_leaves_y_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.y = 0xFF
    cpu.memory[0x0000:0x0002] = (0x8C, 0xCD, 0xAB) #=> STY $ABCD
    cpu.memory[0xABCD] = 0x00
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0xABCD])
    self.assertEquals(0xFF, cpu.y)
    self.assertEquals(flags, cpu.flags)
  
  def test_sty_absolute_stores_y_leaves_y_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.y = 0x00
    cpu.memory[0x0000:0x0002] = (0x8C, 0xCD, 0xAB) #=> STY $ABCD
    cpu.memory[0xABCD] = 0xFF
    cpu.step()
    self.assertEquals(0x0003, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0xABCD])
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(flags, cpu.flags)
  
  # STY Zero Page
  
  def test_sty_zp_stores_y_leaves_y_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.y = 0xFF
    cpu.memory[0x0000:0x0001] = (0x84, 0x10) #=> STY $0010
    cpu.memory[0x0010] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0x0010])
    self.assertEquals(0xFF, cpu.y)
    self.assertEquals(flags, cpu.flags)
  
  def test_sty_zp_stores_y_leaves_y_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.y = 0x00
    cpu.memory[0x0000:0x0001] = (0x84, 0x10) #=> STY $0010
    cpu.memory[0x0010] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010])
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(flags, cpu.flags)
   
  # STY Zero Page, X-Indexed
  
  def test_sty_zp_x_indexed_stores_y_leaves_y_and_n_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.NEGATIVE)
    cpu.y = 0xFF
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x94, 0x10) #=> STY $0010,X
    cpu.memory[0x0010 + cpu.x] = 0x00
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0xFF, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0xFF, cpu.y)
    self.assertEquals(flags, cpu.flags)
  
  def test_sty_zp_x_indexed_stores_y_leaves_y_and_z_flag_unchanged(self):
    cpu = MPU()
    cpu.flags = flags = 0xFF & ~(cpu.ZERO)
    cpu.y = 0x00
    cpu.x = 0x03
    cpu.memory[0x0000:0x0001] = (0x94, 0x10) #=> STY $0010,X
    cpu.memory[0x0010 + cpu.x] = 0xFF
    cpu.step()
    self.assertEquals(0x0002, cpu.pc)
    self.assertEquals(0x00, cpu.memory[0x0010 + cpu.x])
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(flags, cpu.flags)
  
  # TAX
  
  def test_tax_transfers_accumulator_into_x(self):
    cpu = MPU()
    cpu.a = 0xAB
    cpu.x = 0x00
    cpu.memory[0x0000] = 0xAA #=> TAX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB, cpu.a)
    self.assertEquals(0xAB, cpu.x)

  def test_tax_sets_negative_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x80
    cpu.x = 0x00
    cpu.memory[0x0000] = 0xAA #=> TAX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)

  def test_tax_sets_zero_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.x = 0xFF
    cpu.memory[0x0000] = 0xAA #=> TAX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)

  # TAY

  def test_tay_transfers_accumulator_into_y(self):
    cpu = MPU()
    cpu.a = 0xAB
    cpu.y = 0x00
    cpu.memory[0x0000] = 0xA8 #=> TAY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB, cpu.a)
    self.assertEquals(0xAB, cpu.y)

  def test_tay_sets_negative_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.a = 0x80
    cpu.y = 0x00
    cpu.memory[0x0000] = 0xA8 #=> TAY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(0x80, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)

  def test_tay_sets_zero_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.a = 0x00
    cpu.y = 0xFF
    cpu.memory[0x0000] = 0xA8 #=> TAY
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
  
  # TSX
  
  def test_tsx_transfers_stack_pointer_into_x(self):
    cpu = MPU()
    cpu.sp = 0xAB
    cpu.x = 0x00
    cpu.memory[0x0000] = 0xBA #=> TSX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB, cpu.sp)
    self.assertEquals(0xAB, cpu.x)

  def test_tsx_sets_negative_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.sp = 0x80
    cpu.x = 0x00
    cpu.memory[0x0000] = 0xBA #=> TSX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.sp)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)

  def test_tsx_sets_zero_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.sp = 0x00
    cpu.y  = 0xFF
    cpu.memory[0x0000] = 0xBA #=> TSX
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.sp)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
  
  # TXA

  def test_txa_transfers_x_into_a(self):
    cpu = MPU()
    cpu.x = 0xAB
    cpu.a = 0x00
    cpu.memory[0x0000] = 0x8A #=> TXA
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB, cpu.a)
    self.assertEquals(0xAB, cpu.x)

  def test_txa_sets_negative_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.x = 0x80
    cpu.a = 0x00
    cpu.memory[0x0000] = 0x8A #=> TXA
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)

  def test_txa_sets_zero_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.x = 0x00
    cpu.a  = 0xFF
    cpu.memory[0x0000] = 0x8A #=> TXA
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    
  # TXS

  def test_txs_transfers_x_into_stack_pointer(self):
    cpu = MPU()
    cpu.x = 0xAB
    cpu.memory[0x0000] = 0x9A #=> TXS
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB, cpu.sp)
    self.assertEquals(0xAB, cpu.x)

  def test_txs_does_not_set_negative_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.x = 0x80
    cpu.memory[0x0000] = 0x9A #=> TXS
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.sp)
    self.assertEquals(0x80, cpu.x)
    self.assertEquals(0, cpu.flags & cpu.NEGATIVE)

  def test_txs_does_not_set_zero_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.x = 0x00
    cpu.memory[0x0000] = 0x9A #=> TXS
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x00, cpu.sp)
    self.assertEquals(0x00, cpu.x)
    self.assertEquals(0, cpu.flags & cpu.ZERO)

  # TYA

  def test_tya_transfers_y_into_a(self):
    cpu = MPU()
    cpu.y = 0xAB
    cpu.a = 0x00
    cpu.memory[0x0000] = 0x98 #=> TYA
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0xAB, cpu.a)
    self.assertEquals(0xAB, cpu.y)

  def test_tya_sets_negative_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.NEGATIVE)
    cpu.y = 0x80
    cpu.a = 0x00
    cpu.memory[0x0000] = 0x98 #=> TYA
    cpu.step()
    self.assertEquals(0x0001, cpu.pc)
    self.assertEquals(0x80, cpu.a)
    self.assertEquals(0x80, cpu.y)
    self.assertEquals(cpu.NEGATIVE, cpu.flags & cpu.NEGATIVE)
  
  def test_tya_sets_zero_flag(self):
    cpu = MPU()
    cpu.flags &= ~(cpu.ZERO)
    cpu.y = 0x00
    cpu.a  = 0xFF
    cpu.memory[0x0000] = 0x98 #=> TYA
    cpu.step()
    self.assertEquals(0x00, cpu.a)
    self.assertEquals(0x00, cpu.y)
    self.assertEquals(cpu.ZERO, cpu.flags & cpu.ZERO)
    self.assertEquals(0x0001, cpu.pc)
      

  
def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
