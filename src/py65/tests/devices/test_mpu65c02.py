import unittest
import sys
import py65.devices.mpu65c02
from py65.tests.devices.test_mpu6502 import Common6502Tests


class MPUTests(unittest.TestCase, Common6502Tests):
    """CMOS 65C02 Tests"""

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertEquals('<65C02: A=00, X=00, Y=00, Flags=20, SP=ff, PC=0000>',
                          repr(mpu))

    # AND Zero Page, Indirect
    
    def test_and_zp_indirect_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        self._write(mpu.memory, 0x0000, (0x32, 0x10)) #=> AND ($0010)
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB)) #=> Vector to $ABCD
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)
        self.assertEquals(0x00, mpu.a)
        self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
        self.assertEquals(0, mpu.flags & mpu.NEGATIVE)
  
    def test_and_zp_indirect_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        self._write(mpu.memory, 0x0000, (0x32, 0x10)) #=> AND ($0010)
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB)) #=> Vector to $ABCD    
        mpu.memory[0xABCD] = 0xAA
        mpu.step()
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)
        self.assertEquals(0xAA, mpu.a)
        self.assertEquals(mpu.NEGATIVE, mpu.flags & mpu.NEGATIVE)
        self.assertEquals(0, mpu.flags & mpu.ZERO)


    # LDA Zero Page, Indirect

    def test_lda_zp_indirect_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0xB2, 0x10)) #=> LDA ($0010)
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB)) #=> Vector to $ABCD
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)
        self.assertEquals(0x80, mpu.a)
        self.assertEquals(mpu.NEGATIVE, mpu.flags & mpu.NEGATIVE)
        self.assertEquals(0, mpu.flags & mpu.ZERO)

    def test_lda_zp_indirect_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0xB2, 0x10)) #=> LDA ($0010)
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB)) #=> Vector to $ABCD
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)
        self.assertEquals(0x00, mpu.a)
        self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
        self.assertEquals(0, mpu.flags & mpu.NEGATIVE)

    # ORA Zero Page, Indirect
    
    def test_ora_zp_indirect_x_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.flags &= ~(mpu.ZERO)
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0x12, 0x10)) #=> ORA ($0010)
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB)) #=> Vector to $ABCD
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)
        self.assertEquals(0x00, mpu.a)
        self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
          
    def test_ora_zp_indirect_x_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.flags &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        self._write(mpu.memory, 0x0000, (0x12, 0x10)) #=> ORA ($0010)
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB)) #=> Vector to $ABCD
        mpu.memory[0xABCD] = 0x82
        mpu.step()
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)
        self.assertEquals(0x83, mpu.a)
        self.assertEquals(mpu.NEGATIVE, mpu.flags & mpu.NEGATIVE)
        self.assertEquals(0, mpu.flags & mpu.ZERO)

    # PHX
  
    def test_phx_pushes_x_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        mpu.memory[0x0000] = 0xDA #=> PHX
        mpu.step()
        self.assertEquals(0x0001, mpu.pc)
        self.assertEquals(0xAB, mpu.x)
        self.assertEquals(0xAB, mpu.memory[0x01FF])
        self.assertEquals(0xFE, mpu.sp)
        self.assertEquals(3, mpu.processorCycles) 
        
    # PHY
  
    def test_phy_pushes_y_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.y = 0xAB
        mpu.memory[0x0000] = 0x5A #=> PHY
        mpu.step()
        self.assertEquals(0x0001, mpu.pc)
        self.assertEquals(0xAB, mpu.y)
        self.assertEquals(0xAB, mpu.memory[0x01FF])
        self.assertEquals(0xFE, mpu.sp)
        self.assertEquals(3, mpu.processorCycles)

    # PLX
    
    def test_plx_pulls_top_byte_from_stack_into_x_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0xFA #=> PLX
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEquals(0x0001, mpu.pc)
        self.assertEquals(0xAB,   mpu.x)
        self.assertEquals(0xFF,   mpu.sp)
        self.assertEquals(4, mpu.processorCycles)
        
    # PLY
    
    def test_ply_pulls_top_byte_from_stack_into_y_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x7A #=> PLY
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEquals(0x0001, mpu.pc)
        self.assertEquals(0xAB,   mpu.y)
        self.assertEquals(0xFF,   mpu.sp)
        self.assertEquals(4, mpu.processorCycles) 
        
    # STZ Zero Page

    def test_stz_zp_stores_zero(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0x0032] = 0x88
        mpu.memory[0x0000:0x0000+2] = [0x64, 0x32] #=> STZ $32
        self.assertEquals(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEquals(0x00, mpu.memory[0x0032])
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(3, mpu.processorCycles)

    # STZ Zero Page, X-Indexed

    def test_stz_zp_x_stores_zero(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0x0032] = 0x88
        mpu.memory[0x0000:0x0000+2] = [0x74, 0x32] #=> STZ $32,X
        self.assertEquals(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEquals(0x00, mpu.memory[0x0032])
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(4, mpu.processorCycles)

    # STZ Absolute

    def test_stz_abs_stores_zero(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0xFEED] = 0x88
        mpu.memory[0x0000:0x0000+3] = [0x9C, 0xED, 0xFE] #=> STZ $FEED
        self.assertEquals(0x88, mpu.memory[0xFEED])
        mpu.step()
        self.assertEquals(0x00, mpu.memory[0xFEED])
        self.assertEquals(0x0003, mpu.pc)
        self.assertEquals(4, mpu.processorCycles)

    # STZ Absolute, X-Indexed

    def test_stz_abs_stores_zero(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0xFEED] = 0x88
        mpu.x = 0x0D
        mpu.memory[0x0000:0x0000+3] = [0x9E, 0xE0, 0xFE] #=> STZ $FEE0,X
        self.assertEquals(0x88, mpu.memory[0xFEED])
        self.assertEquals(0x0D, mpu.x)
        mpu.step()
        self.assertEquals(0x00, mpu.memory[0xFEED])
        self.assertEquals(0x0003, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)
 
    # TSB Zero Page

    def test_tsb_sp_ones(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0x00BB] = 0xE0
        self._write(mpu.memory, 0x0000, [0x04, 0xBB]) #=> TSB $BD
        mpu.a = 0x70
        self.assertEquals(0xE0, mpu.memory[0x00BB])
        mpu.step()
        self.assertEquals(0xF0, mpu.memory[0x00BB])
        self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)

    def test_tsb_sp_zeros(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0x00BB] = 0x80
        self._write(mpu.memory, 0x0000, [0x04, 0xBB]) #=> TSB $BD
        mpu.a = 0x60
        self.assertEquals(0x80, mpu.memory[0x00BB])
        mpu.step()
        self.assertEquals(0xE0, mpu.memory[0x00BB])
        self.assertEquals(0, mpu.flags & mpu.ZERO)
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)


    # TSB Absolute

    def test_tsb_abs_ones(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0xFEED] = 0xE0
        self._write(mpu.memory, 0x0000, [0x0C, 0xED, 0xFE]) #=> TSB $FEED
        mpu.a = 0x70
        self.assertEquals(0xE0, mpu.memory[0xFEED])
        mpu.step()
        self.assertEquals(0xF0, mpu.memory[0xFEED])
        self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
        self.assertEquals(0x0003, mpu.pc)
        self.assertEquals(6, mpu.processorCycles)

    def test_tsb_abs_zeros(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0xFEED] = 0x80
        self._write(mpu.memory, 0x0000, [0x0C, 0xED, 0xFE]) #=> TSB $FEED
        mpu.a = 0x60
        self.assertEquals(0x80, mpu.memory[0xFEED])
        mpu.step()
        self.assertEquals(0xE0, mpu.memory[0xFEED])
        self.assertEquals(0, mpu.flags & mpu.ZERO)
        self.assertEquals(0x0003, mpu.pc)
        self.assertEquals(6, mpu.processorCycles)

    # TRB Zero Page

    def test_trb_sp_ones(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0x00BB] = 0xE0
        self._write(mpu.memory, 0x0000, [0x14, 0xBB]) #=> TRB $BD
        mpu.a = 0x70
        self.assertEquals(0xE0, mpu.memory[0x00BB])
        mpu.step()
        self.assertEquals(0x80, mpu.memory[0x00BB])
        self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)

    def test_trb_sp_zeros(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0x00BB] = 0x80
        self._write(mpu.memory, 0x0000, [0x14, 0xBB]) #=> TRB $BD
        mpu.a = 0x60
        self.assertEquals(0x80, mpu.memory[0x00BB])
        mpu.step()
        self.assertEquals(0x80, mpu.memory[0x00BB])
        self.assertEquals(0, mpu.flags & mpu.ZERO)
        self.assertEquals(0x0002, mpu.pc)
        self.assertEquals(5, mpu.processorCycles)


    # TRB Absolute

    def test_trb_abs_ones(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0xFEED] = 0xE0
        self._write(mpu.memory, 0x0000, [0x1C, 0xED, 0xFE]) #=> TRB $FEED
        mpu.a = 0x70
        self.assertEquals(0xE0, mpu.memory[0xFEED])
        mpu.step()
        self.assertEquals(0x80, mpu.memory[0xFEED])
        self.assertEquals(mpu.ZERO, mpu.flags & mpu.ZERO)
        self.assertEquals(0x0003, mpu.pc)
        self.assertEquals(6, mpu.processorCycles)

    def test_trb_abs_zeros(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0xFEED] = 0x80
        self._write(mpu.memory, 0x0000, [0x1C, 0xED, 0xFE]) #=> TRB $FEED
        mpu.a = 0x60
        self.assertEquals(0x80, mpu.memory[0xFEED])
        mpu.step()
        self.assertEquals(0x80, mpu.memory[0xFEED])
        self.assertEquals(0, mpu.flags & mpu.ZERO)
        self.assertEquals(0x0003, mpu.pc)
        self.assertEquals(6, mpu.processorCycles)


    # Test Helpers

    def _get_target_class(self):
        return py65.devices.mpu65c02.MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
