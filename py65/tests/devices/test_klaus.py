import unittest
import sys
import py65.devices.mpu65c02

class KlausDormannTests(unittest.TestCase):
    """Runs Klaus Dormann's 6502-based test suites"""

    def klausTestCase(self, filename, load_addr, pc, success_addr, should_trace=None):
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

    def test6502FunctionalTest(self):
        self.klausTestCase("6502_functional_test.bin", 0x0, 0x400, 0x3399)

    def test65C02ExtendedOpcodesTest(self):
        tracer = lambda pc: (0x1484 <= pc <= 0x16cc)
        self.klausTestCase("65C02_extended_opcodes_test_modified.bin", 0xa, 0x400, 0x24a8, tracer)

    def test6502DecimalTest(self):
        mpu = self._make_mpu()
        mpu.pc = 0x1000

        object_code = bytearray(open("6502_decimal_test.bin", "r").read())
        self._write(mpu.memory, 0x200, object_code)

        # $1000: JSR $0200
        self._write(mpu.memory, 0x1000, [0x20, 0x00, 0x02])

        while True:
            mpu.step()
            if mpu.pc == 0x1003:
                break
        assert mpu.memory[0x0b] == 0

    # Test Helpers

    def _write(self, memory, start_address, bytes):
        memory[start_address:start_address + len(bytes)] = bytes

    def _make_mpu(self, *args, **kargs):
        klass = self._get_target_class()
        mpu = klass(*args, **kargs)
        if 'memory' not in kargs:
            mpu.memory = 0x10000 * [0xAA]
        return mpu

    def _get_target_class(self):
        return py65.devices.mpu65c02.MPU

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
