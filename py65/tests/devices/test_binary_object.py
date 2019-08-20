import unittest
import sys
import py65.devices.mpu6502
import py65.devices.mpu65c02


class BinaryObjectTests(unittest.TestCase):
    """Test cases based on executing 65x02 object code."""

    # If test fails, rerun with execution tracing enabled
    TRACE_TEST_FAILURE = False

    def binaryObjectTestCase(self, filename, load_addr, pc, success_addr, should_trace=None):
        mpu = self._make_mpu()
        mpu.pc = pc

        object_code = bytearray(open(filename, "r").read())
        self._write(mpu.memory, load_addr, object_code)

        if not should_trace:
            should_trace = lambda pc: False

        while True:
            old_pc = mpu.pc
            mpu.step(trace=should_trace(mpu.pc))
            if mpu.pc == old_pc:
                break

        assert mpu.pc == success_addr, "%s 0xb=%02x 0xc=%02x 0xd=%02x 0xf=%02x" % (
            mpu, mpu.memory[0xb], mpu.memory[0xc], mpu.memory[0xd], mpu.memory[0xf])

    # Test Helpers

    def _write(self, memory, start_address, bytes):
        memory[start_address:start_address + len(bytes)] = bytes

    def _make_mpu(self, *args, **kargs):
        mpu = self.MPU(*args, **kargs)
        if 'memory' not in kargs:
            mpu.memory = 0x10000 * [0xAA]
        return mpu

    def runBinaryTest(self, executor, filename):
        try:
            return executor(filename)
        except AssertionError:
            # Rerun with tracing
            if self.TRACE_TEST_FAILURE:
                return executor(filename, trace=True)
            else:
                raise


class FunctionalBCDTests(BinaryObjectTests):
    def bcd_test_case(self, filename, trace=False):
        mpu = self._make_mpu()
        mpu.pc = 0x1000

        object_code = bytearray(open(filename, "r").read())
        self._write(mpu.memory, 0x200, object_code)

        # $1000: JSR $0200
        self._write(mpu.memory, 0x1000, [0x20, 0x00, 0x02])

        # Set up BRK vector pointing to $2000 so we can trap PC
        self._write(mpu.memory, 0xfffe, [0x00, 0x20])

        def should_trace(pc):
            return trace

        while True:
            old_pc = mpu.pc
            mpu.step(trace=should_trace(mpu.pc))
            # If we are looping at the same PC, or we return
            # from the JSR, or we hit the BRK vector, then we are done.
            if mpu.pc == old_pc or mpu.pc == 0x1003 or mpu.pc == 0x2000:
                break

        if mpu.memory[0x0b] != 0:  # Tests did not complete successfully
            assert False, ("N1={:02x} N2={:02x} HA={:02x} HNVZC={:08b} DA={"
                           ":02x} DNVZC={:08b} AR={:02x} NF={:08b} VF={:08b} "
                           "ZF={:08b} CF={:08b}".format(
                mpu.memory[0x00], mpu.memory[0x01], mpu.memory[0x02],
                mpu.memory[0x03], mpu.memory[0x04], mpu.memory[0x05],
                mpu.memory[0x06], mpu.memory[0x07], mpu.memory[0x08],
                mpu.memory[0x09], mpu.memory[0x0a]
            ))


class Functional6502Tests(FunctionalBCDTests):
    MPU = py65.devices.mpu6502.MPU

    def test6502DecimalTest(self):
        self.runBinaryTest(
            self.bcd_test_case, "devices/bcd/6502_decimal_test.bin")


class Functional65C02Tests(FunctionalBCDTests):
    MPU = py65.devices.mpu65c02.MPU

    def test65C02DecimalTest(self):
        self.runBinaryTest(
            self.bcd_test_case, "devices/bcd/65C02_decimal_test.bin")


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
