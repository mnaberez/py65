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

    def test_stz_zp_stores_zero(self):
        mpu = self._make_mpu(debug=True)
        mpu.memory[0x0032] = 0x88
        mpu.memory[0x0000:0x0000+2] = [0x64, 0x32] #=> STZ $32
        self.assertEquals(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEquals(0x00, mpu.memory[0x0032])
        self.assertEquals(3, mpu.processorCycles)

    # Test Helpers

    def _get_target_class(self):
        return py65.devices.mpu65c02.MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
