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
 


    # Test Helpers

    def _get_target_class(self):
        return py65.devices.mpu65c02.MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
