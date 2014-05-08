import unittest
import sys
import py65.devices.mpu65c02
from py65.tests.devices.test_mpu6502 import Common6502Tests


class MPUTests(unittest.TestCase, Common6502Tests):
    """CMOS 65C02 Tests"""

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue('65C02' in repr(mpu))

    # ADC Zero Page, Indirect

    def test_adc_bcd_off_zp_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_ind_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_zp_ind_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFE
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_ind_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_ind_overflow_cleared_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_ind_overflow_cleared_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_ind_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_ind_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_ind_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x40
        # $0000 ADC ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x72, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Zero Page, Indirect

    def test_and_zp_ind_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x32, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_zp_ind_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x32, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xAA
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # BIT (Absolute, X-Indexed)

    def test_bit_abs_x_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_stores_result_of_and_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x01
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0xFEED])
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    def test_bit_abs_x_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x02
        # $0000 BIT $FEEB,X
        self._write(mpu.memory, 0x0000, (0x3C, 0xEB, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x0003, mpu.pc)

    # BIT (Immediate)

    def test_bit_imm_does_not_affect_n_and_z_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE | mpu.OVERFLOW
        # $0000 BIT #$FF
        self._write(mpu.memory, 0x0000, (0x89, 0xff))
        mpu.a = 0x00
        mpu.step()
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x02, mpu.pc)

    def test_bit_imm_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT #$00
        self._write(mpu.memory, 0x0000, (0x89, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x02, mpu.pc)

    def test_bit_imm_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT #$01
        self._write(mpu.memory, 0x0000, (0x89, 0x01))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x02, mpu.pc)

    def test_bit_imm_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT #$00
        self._write(mpu.memory, 0x0000, (0x89, 0x00))
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(2, mpu.processorCycles)
        self.assertEqual(0x02, mpu.pc)

    # BIT (Zero Page, X-Indexed)

    def test_bit_zp_x_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0xFF
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_bit_zp_x_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x00
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_bit_zp_x_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0xFF
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_bit_zp_x_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x00
        mpu.x = 0x03
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_bit_zp_x_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x00
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])

    def test_bit_zp_x_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x01
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x])

    def test_bit_zp_x_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT $0010,X
        self._write(mpu.memory, 0x0000, (0x34, 0x10))
        mpu.memory[0x0013] = 0x00
        mpu.x = 0x03
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])

    # BRK

    def test_brk_clears_decimal_flag(self):
        mpu = self._make_mpu()
        mpu.p = mpu.DECIMAL
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(0, mpu.p & mpu.DECIMAL)

    # CMP Zero Page, Indirect

    def test_cmp_zpi_sets_z_flag_if_equal(self):
        mpu = self._make_mpu()
        mpu.a = 0x42
        # $0000 AND ($10)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xd2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x42
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x42, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_cmp_zpi_resets_z_flag_if_unequal(self):
        mpu = self._make_mpu()
        mpu.a = 0x43
        # $0000 AND ($10)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xd2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x42
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x43, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # EOR Zero Page, Indirect

    def test_eor_zp_ind_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 EOR ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x52, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_zp_ind_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 EOR ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x52, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # INC Accumulator

    def test_inc_acc_increments_accum(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0x42
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x43, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_acc_increments_accum_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_acc_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.memory[0x0000] = 0x1A
        mpu.a = 0x7F
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # JMP Indirect

    def test_jmp_ind_does_not_have_page_wrap_bug(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x10FF, (0xCD, 0xAB))
        # $0000 JMP ($10FF)
        self._write(mpu.memory, 0, (0x6c, 0xFF, 0x10))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    # JMP Indirect Absolute X-Indexed

    def test_jmp_iax_jumps_to_address(self):
        mpu = self._make_mpu()
        mpu.x = 2
        # $0000 JMP ($ABCD,X)
        # $ABCF Vector to $1234
        self._write(mpu.memory, 0x0000, (0x7C, 0xCD, 0xAB))
        self._write(mpu.memory, 0xABCF, (0x34, 0x12))
        mpu.step()
        self.assertEqual(0x1234, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    # LDA Zero Page, Indirect

    def test_lda_zp_ind_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_zp_ind_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB2, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # ORA Zero Page, Indirect

    def test_ora_zp_ind_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x12  # These should not affect the ORA
        mpu.x = 0x34
        # $0000 ORA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x12, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_zp_ind_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        # $0000 ORA ($0010)
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x12, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # PHX

    def test_phx_pushes_x_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        # $0000 PHX
        mpu.memory[0x0000] = 0xDA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.x)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xFE, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PHY

    def test_phy_pushes_y_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.y = 0xAB
        # $0000 PHY
        mpu.memory[0x0000] = 0x5A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.y)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xFE, mpu.sp)
        self.assertEqual(3, mpu.processorCycles)

    # PLX

    def test_plx_pulls_top_byte_from_stack_into_x_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLX
        mpu.memory[0x0000] = 0xFA
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.x)
        self.assertEqual(0xFF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # PLY

    def test_ply_pulls_top_byte_from_stack_into_y_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLY
        mpu.memory[0x0000] = 0x7A
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.y)
        self.assertEqual(0xFF,   mpu.sp)
        self.assertEqual(4, mpu.processorCycles)

    # RMB0

    def test_rmb0_clears_bit_0_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB0 $43
        self._write(mpu.memory, 0x0000, (0x07, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('11111110', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_rmb0_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB0 $43
        self._write(mpu.memory, 0x0000, (0x07, 0x43))
        expected = int('01010101', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # RMB1

    def test_rmb1_clears_bit_1_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB1 $43
        self._write(mpu.memory, 0x0000, (0x17, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('11111101', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_rmb1_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB1 $43
        self._write(mpu.memory, 0x0000, (0x17, 0x43))
        expected = int('01010101', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # RMB2

    def test_rmb2_clears_bit_2_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB2 $43
        self._write(mpu.memory, 0x0000, (0x27, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('11111011', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_rmb2_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB2 $43
        self._write(mpu.memory, 0x0000, (0x27, 0x43))
        expected = int('01010101', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # RMB3

    def test_rmb3_clears_bit_3_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB3 $43
        self._write(mpu.memory, 0x0000, (0x37, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('11110111', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_rmb3_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB3 $43
        self._write(mpu.memory, 0x0000, (0x37, 0x43))
        expected = int('01010101', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # RMB4

    def test_rmb4_clears_bit_4_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB4 $43
        self._write(mpu.memory, 0x0000, (0x47, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('11101111', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_rmb4_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB4 $43
        self._write(mpu.memory, 0x0000, (0x47, 0x43))
        expected = int('01010101', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # RMB5

    def test_rmb5_clears_bit_5_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB5 $43
        self._write(mpu.memory, 0x0000, (0x57, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('11011111', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_rmb5_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB5 $43
        self._write(mpu.memory, 0x0000, (0x57, 0x43))
        expected = int('01010101', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # RMB6

    def test_rmb6_clears_bit_6_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB6 $43
        self._write(mpu.memory, 0x0000, (0x67, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('10111111', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_rmb6_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB6 $43
        self._write(mpu.memory, 0x0000, (0x67, 0x43))
        expected = int('01010101', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # RMB7

    def test_rmb7_clears_bit_7_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB7 $43
        self._write(mpu.memory, 0x0000, (0x77, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('01111111', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_rmb7_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('11111111', 2)
        # $0000 RMB7 $43
        self._write(mpu.memory, 0x0000, (0x77, 0x43))
        expected = int('01010101', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # STA Zero Page, Indirect

    def test_sta_zp_ind_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        # $0000 STA ($0010)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x92, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0xFF, mpu.memory[0xFEED])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_zp_ind_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA ($0010)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x92, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # SMB0

    def test_smb0_sets_bit_0_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB0 $43
        self._write(mpu.memory, 0x0000, (0x87, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('00000001', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_smb0_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB0 $43
        self._write(mpu.memory, 0x0000, (0x87, 0x43))
        expected = int('11001100', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # SMB1

    def test_smb1_sets_bit_1_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB1 $43
        self._write(mpu.memory, 0x0000, (0x97, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('00000010', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_smb1_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB1 $43
        self._write(mpu.memory, 0x0000, (0x97, 0x43))
        expected = int('11001100', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # SMB2

    def test_smb2_sets_bit_2_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB2 $43
        self._write(mpu.memory, 0x0000, (0xA7, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('00000100', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_smb2_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB2 $43
        self._write(mpu.memory, 0x0000, (0xA7, 0x43))
        expected = int('11001100', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # SMB3

    def test_smb3_sets_bit_3_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB3 $43
        self._write(mpu.memory, 0x0000, (0xB7, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('00001000', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_smb3_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB3 $43
        self._write(mpu.memory, 0x0000, (0xB7, 0x43))
        expected = int('11001100', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # SMB4

    def test_smb4_sets_bit_4_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB4 $43
        self._write(mpu.memory, 0x0000, (0xC7, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('00010000', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_smb4_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB4 $43
        self._write(mpu.memory, 0x0000, (0xC7, 0x43))
        expected = int('11001100', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # SMB5

    def test_smb5_sets_bit_5_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB5 $43
        self._write(mpu.memory, 0x0000, (0xD7, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('00100000', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_smb5_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB5 $43
        self._write(mpu.memory, 0x0000, (0xD7, 0x43))
        expected = int('11001100', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # SMB6

    def test_smb6_sets_bit_6_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB6 $43
        self._write(mpu.memory, 0x0000, (0xE7, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('01000000', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_smb6_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB6 $43
        self._write(mpu.memory, 0x0000, (0xE7, 0x43))
        expected = int('11001100', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # SMB7

    def test_smb7_sets_bit_7_without_affecting_other_bits(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB7 $43
        self._write(mpu.memory, 0x0000, (0xF7, 0x43))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        expected = int('10000000', 2)
        self.assertEqual(expected, mpu.memory[0x0043])

    def test_smb7_does_not_affect_status_register(self):
        mpu = self._make_mpu()
        mpu.memory[0x0043] = int('00000000', 2)
        # $0000 SMB7 $43
        self._write(mpu.memory, 0x0000, (0xF7, 0x43))
        expected = int('11001100', 2)
        mpu.p = expected
        mpu.step()
        self.assertEqual(expected, mpu.p)

    # SBC Zero Page, Indirect

    def test_sbc_zp_ind_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_ind_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_ind_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_ind_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10)
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF2, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x02
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # STZ Zero Page

    def test_stz_zp_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0x0032] = 0x88
        # #0000 STZ $32
        mpu.memory[0x0000:0x0000 + 2] = [0x64, 0x32]
        self.assertEqual(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0x0032])
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)

    # STZ Zero Page, X-Indexed

    def test_stz_zp_x_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0x0032] = 0x88
        # $0000 STZ $32,X
        mpu.memory[0x0000:0x0000 + 2] = [0x74, 0x32]
        self.assertEqual(0x88, mpu.memory[0x0032])
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0x0032])
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)

    # STZ Absolute

    def test_stz_abs_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0x88
        # $0000 STZ $FEED
        mpu.memory[0x0000:0x0000 + 3] = [0x9C, 0xED, 0xFE]
        self.assertEqual(0x88, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(4, mpu.processorCycles)

    # STZ Absolute, X-Indexed

    def test_stz_abs_x_stores_zero(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0x88
        mpu.x = 0x0D
        # $0000 STZ $FEE0,X
        mpu.memory[0x0000:0x0000 + 3] = [0x9E, 0xE0, 0xFE]
        self.assertEqual(0x88, mpu.memory[0xFEED])
        self.assertEqual(0x0D, mpu.x)
        mpu.step()
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # TSB Zero Page

    def test_tsb_sp_ones(self):
        mpu = self._make_mpu()
        mpu.memory[0x00BB] = 0xE0
        # $0000 TSB $BD
        self._write(mpu.memory, 0x0000, [0x04, 0xBB])
        mpu.a = 0x70
        self.assertEqual(0xE0, mpu.memory[0x00BB])
        mpu.step()
        self.assertEqual(0xF0, mpu.memory[0x00BB])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    def test_tsb_sp_zeros(self):
        mpu = self._make_mpu()
        mpu.memory[0x00BB] = 0x80
        # $0000 TSB $BD
        self._write(mpu.memory, 0x0000, [0x04, 0xBB])
        mpu.a = 0x60
        self.assertEqual(0x80, mpu.memory[0x00BB])
        mpu.step()
        self.assertEqual(0xE0, mpu.memory[0x00BB])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # TSB Absolute

    def test_tsb_abs_ones(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0xE0
        # $0000 TSB $FEED
        self._write(mpu.memory, 0x0000, [0x0C, 0xED, 0xFE])
        mpu.a = 0x70
        self.assertEqual(0xE0, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0xF0, mpu.memory[0xFEED])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    def test_tsb_abs_zeros(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0x80
        # $0000 TSB $FEED
        self._write(mpu.memory, 0x0000, [0x0C, 0xED, 0xFE])
        mpu.a = 0x60
        self.assertEqual(0x80, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0xE0, mpu.memory[0xFEED])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    # TRB Zero Page

    def test_trb_sp_ones(self):
        mpu = self._make_mpu()
        mpu.memory[0x00BB] = 0xE0
        # $0000 TRB $BD
        self._write(mpu.memory, 0x0000, [0x14, 0xBB])
        mpu.a = 0x70
        self.assertEqual(0xE0, mpu.memory[0x00BB])
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0x00BB])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    def test_trb_sp_zeros(self):
        mpu = self._make_mpu()
        mpu.memory[0x00BB] = 0x80
        # $0000 TRB $BD
        self._write(mpu.memory, 0x0000, [0x14, 0xBB])
        mpu.a = 0x60
        self.assertEqual(0x80, mpu.memory[0x00BB])
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0x00BB])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # TRB Absolute

    def test_trb_abs_ones(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0xE0
        # $0000 TRB $FEED
        self._write(mpu.memory, 0x0000, [0x1C, 0xED, 0xFE])
        mpu.a = 0x70
        self.assertEqual(0xE0, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0xFEED])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    def test_trb_abs_zeros(self):
        mpu = self._make_mpu()
        mpu.memory[0xFEED] = 0x80
        # $0000 TRB $FEED
        self._write(mpu.memory, 0x0000, [0x1C, 0xED, 0xFE])
        mpu.a = 0x60
        self.assertEqual(0x80, mpu.memory[0xFEED])
        mpu.step()
        self.assertEqual(0x80, mpu.memory[0xFEED])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(6, mpu.processorCycles)

    def test_dec_a_decreases_a(self):
        mpu = self._make_mpu()
        # $0000 DEC A
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x48
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0x47, mpu.a)

    def test_dec_a_sets_zero_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC A
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0x00, mpu.a)

    def test_dec_a_wraps_at_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC A
        self._write(mpu.memory, 0x0000, [0x3A])
        mpu.a = 0x00
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0xFF, mpu.a)

    def test_bra_forward(self):
        mpu = self._make_mpu()
        # $0000 BRA $10
        self._write(mpu.memory, 0x0000, [0x80, 0x10])
        mpu.step()
        self.assertEqual(0x12, mpu.pc)
        self.assertEqual(2, mpu.processorCycles)

    def test_bra_backward(self):
        mpu = self._make_mpu()
        # $0240 BRA $F0
        self._write(mpu.memory, 0x0204, [0x80, 0xF0])
        mpu.pc = 0x0204
        mpu.step()
        self.assertEqual(0x1F6, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)  # Crossed boundry

    # Test Helpers

    def _get_target_class(self):
        return py65.devices.mpu65c02.MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
