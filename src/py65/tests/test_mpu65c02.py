import unittest
import sys
from py65.mpu65c02 import MPU

from test_mpu6502 import make_common_tests

MPUTests = make_common_tests(MPU)

class MPU65C02SpecificTests(unittest.TestCase):

    def test_repr(self):
        mpu = MPU()
        self.assertEquals('<65C02: A=00, X=00, Y=00, Flags=20, SP=ff, PC=0000>',
                          repr(mpu))

    def test_stz_zp_stores_zero(self):
        mpu = MPU(debug=True)
        mpu.memory[0x0032] = 0x88
        mpu.memory[0x0000:0x0000+2] = [0x64, 0x32] #=> STZ $32
        self.assertEquals(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEquals(0x00, mpu.memory[0x0032])
        self.assertEquals(3, mpu.processorCycles)


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
