"""65(c)02-based test suite for BCD implementation correctness.

See source code in bcd/*.c65 for more details.
"""

import sys
import unittest

import py65.devices.mpu6502
import py65.devices.mpu65c02
from py65.tests.devices import functional_tests


def run_bcd_test_case(mpu_class, filename, trace=False):
    executor = functional_tests.FunctionalTestExecutor(
        mpu_class, filename, load_addr=0x200)

    # $1000: JSR $0200
    executor.write_memory(0x1000, [0x20, 0x00, 0x02])

    # Set up BRK vector pointing to $2000 so we can trap PC
    executor.write_memory(0xfffe, [0x00, 0x20])

    if trace:
        tracer = executor.always_trace_predicate
    else:
        tracer = executor.never_trace_predicate

    executor.execute(
        0x1000,
        # If we are looping at the same PC, or we return
        # from the JSR, or we hit the BRK vector, then we are done.
        executor.address_completion_predicate({0x1003, 0x2000}),
        tracer
    )
    mpu = executor.mpu

    if mpu.memory[0x0b] != 0:  # Tests did not complete successfully
        # Display internal test state; read the .c65 source to understand
        # what these mean about the particular test case that failed.
        assert False, (
            "N1={:02x} N2={:02x} HA={:02x} HNVZC={:08b} DA={:02x} "
            "DNVZC={:08b} AR={:02x} NF={:08b} VF={:08b} ZF={:08b} "
            "CF={:08b}".format(
                mpu.memory[0x00], mpu.memory[0x01], mpu.memory[0x02],
                mpu.memory[0x03], mpu.memory[0x04], mpu.memory[0x05],
                mpu.memory[0x06], mpu.memory[0x07], mpu.memory[0x08],
                mpu.memory[0x09], mpu.memory[0x0a]
            ))


class BCDFunctionalTests(unittest.TestCase):

    @staticmethod
    def test6502DecimalTest():
        functional_tests.trace_on_assertion(
            run_bcd_test_case,
            py65.devices.mpu6502.MPU,
            "devices/bcd/6502_decimal_test.bin"
        )

    @staticmethod
    def test65c02DecimalTest():
        functional_tests.trace_on_assertion(
            run_bcd_test_case,
            py65.devices.mpu65c02.MPU,
            "devices/bcd/65C02_decimal_test.bin"
        )


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
