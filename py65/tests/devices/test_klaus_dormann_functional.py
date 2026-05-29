"""Harness for running Klaus Dormann's 65(c)02 functional test suite

These are quite comprehensive test suites for 65(c)02 implementation
correctness, but they're licensed under the GPL so we cannot include
the binary object code here (this is just the test harness for executing
them in py65).

Obtain the object files from
https://github.com/Klaus2m5/6502_65C02_functional_tests instead.
"""

import os.path
import sys
import unittest

import py65.devices.mpu6502
import py65.devices.mpu65c02
from py65.tests.devices import functional_tests


def run_klaus_dormann_test(mpu_class, filename, load_addr, success_addr,
                           trace=False):
    executor = functional_tests.FunctionalTestExecutor(
        mpu_class, filename, load_addr)

    if trace:
        tracer = executor.always_trace_predicate
    else:
        tracer = executor.never_trace_predicate

    executor.execute(
        0x400, executor.address_completion_predicate({success_addr}), tracer)

    mpu = executor.mpu
    assert mpu.pc == success_addr, (
            "%s 0xb=%02x 0xc=%02x 0xd=%02x 0xf=%02x" % (
        mpu, mpu.memory[0xb], mpu.memory[0xc], mpu.memory[0xd],
        mpu.memory[0xf])
    )


class KlausDormannTests(unittest.TestCase):
    """Runs Klaus Dormann's 6502-based test suites"""

    def test6502FunctionalTest(self):
        filename = "devices/6502_functional_test.bin"
        if not os.path.exists(filename):
            self.skipTest("%s not available, skipping")

        functional_tests.trace_on_assertion(
            run_klaus_dormann_test,
            py65.devices.mpu6502.MPU,
            filename,
            load_addr=0x0,
            success_addr=0x3399
        )

    def test65c02ExtendedOpcodeTest(self):
        # Modified version of 65C02_extended_opcodes_test that defines
        # rkwl_wdc_op = 0 (don't test BBR/BBS instructions, which we do not
        # implement) and many of the NOP tests for undefined opcodes which
        # are not yet implemented here.
        filename = "devices/65C02_extended_opcodes_test_modified.bin"

        if not os.path.exists(filename):
            self.skipTest("%s not available, skipping")

        functional_tests.trace_on_assertion(
            run_klaus_dormann_test,
            py65.devices.mpu65c02.MPU,
            filename,
            load_addr=0xa,
            success_addr=0x1570
        )


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
