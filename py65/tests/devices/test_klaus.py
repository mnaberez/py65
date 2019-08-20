import unittest
import sys
import py65.devices.mpu65c02


class KlausDormannTests(unittest.TestCase):
    """Runs Klaus Dormann's 6502-based test suites"""

    MPU = py65.devices.mpu65c02.MPU

    def klausTestCase(self, filename, load_addr, pc, completion_criteria,
                      should_trace=None):
        mpu = self._make_mpu()
        mpu.pc = pc

        object_code = bytearray(open(filename, "r").read())
        self._write(mpu.memory, load_addr, object_code)

        if not should_trace:
            should_trace = lambda pc: False

        while True:
            old_pc = mpu.pc
            mpu.step(trace=should_trace(mpu.pc))
            if completion_criteria(mpu, old_pc):
                break

        return mpu

    def make_completion_criteria(self, success_addr):
        def completion_criteria(mpu, old_pc):
            return mpu.pc == old_pc or mpu.pc == success_addr

        return completion_criteria

    def test6502FunctionalTest(self):
        success_addr = 0x3399
        completion_criteria = self.make_completion_criteria(success_addr)

        mpu = self.klausTestCase(
            "devices/6502_functional_test.bin", 0x0, 0x400,
            completion_criteria
        )

        assert mpu.pc == success_addr, (
                "%s 0xb=%02x 0xc=%02x 0xd=%02x 0xf=%02x" % (
            mpu, mpu.memory[0xb], mpu.memory[0xc], mpu.memory[0xd],
            mpu.memory[0xf])
        )

    def test65C02ExtendedOpcodesTest(self):
        success_addr = 0x1570
        completion_criteria = self.make_completion_criteria(success_addr)

        # Modified version of 65C02_extended_opcodes_test that defines
        # rkwl_wdc_op = 0 (don't test BBR/BBS instructions, which we do not
        # implement) and many of the NOP tests for undefined opcodes which are
        # not yet implemented here.
        mpu = self.klausTestCase(
            "devices/65C02_extended_opcodes_test_modified.bin", 0xa, 0x400,
            completion_criteria
        )

        assert mpu.pc == success_addr, (
                "%s 0xb=%02x 0xc=%02x 0xd=%02x 0xf=%02x" % (
            mpu, mpu.memory[0xb], mpu.memory[0xc], mpu.memory[0xd],
            mpu.memory[0xf])
        )

    # Test Helpers

    def _write(self, memory, start_address, bytes):
        memory[start_address:start_address + len(bytes)] = bytes

    def _make_mpu(self, *args, **kargs):
        mpu = self.MPU(*args, **kargs)
        if 'memory' not in kargs:
            mpu.memory = 0x10000 * [0xAA]
        return mpu


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
