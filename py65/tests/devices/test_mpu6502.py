import unittest
import sys
import py65.assembler
import py65.devices.mpu6502


class Common6502Tests:
    """Tests common to 6502-based microprocessors"""

    # Reset

    def test_reset_sets_registers_to_initial_states(self):
        mpu = self._make_mpu()
        mpu.reset()
        self.assertEqual(0xFF, mpu.sp)
        self.assertEqual(0, mpu.a)
        self.assertEqual(0, mpu.x)
        self.assertEqual(0, mpu.y)
        self.assertEqual(mpu.BREAK | mpu.UNUSED, mpu.p)

    # ADC Absolute

    def test_adc_bcd_off_absolute_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        self.assertEqual(0x10000, len(mpu.memory))

        mpu.memory[0xC000] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.memory[0xC000] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_absolute_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.memory[0xC000] = 0xFE
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.memory[0xC000] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.memory[0xC000] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.memory[0xC000] = 0xff
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.memory[0xC000] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.memory[0xC000] = 0xff
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_absolute_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x40
        # $0000 ADC $C000
        self._write(mpu.memory, 0x0000, (0x6D, 0x00, 0xC0))
        mpu.memory[0xC000] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Zero Page

    def test_adc_bcd_off_zp_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_zp_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0xFE
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0xff
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0xff
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x40
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 ADC $00B0
        self._write(mpu.memory, 0x0000, (0x65, 0xB0))
        mpu.memory[0x00B0] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Immediate

    def test_adc_bcd_off_immediate_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0
        # $0000 ADC #$00
        self._write(mpu.memory, 0x0000, (0x69, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.p |= mpu.CARRY
        # $0000 ADC #$00
        self._write(mpu.memory, 0x0000, (0x69, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_immediate_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        # $0000 ADC #$FE
        self._write(mpu.memory, 0x0000, (0x69, 0xFE))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        # $0000 ADC #$FF
        self._write(mpu.memory, 0x0000, (0x69, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC #$01
        self._write(mpu.memory, 0x000, (0x69, 0x01))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC #$FF
        self._write(mpu.memory, 0x000, (0x69, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        # $0000 ADC #$01
        self._write(mpu.memory, 0x000, (0x69, 0x01))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        # $0000 ADC #$FF
        self._write(mpu.memory, 0x000, (0x69, 0xff))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_immediate_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.a = 0x40
        # $0000 ADC #$40
        self._write(mpu.memory, 0x0000, (0x69, 0x40))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_on_immediate_79_plus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x79
        # $0000 ADC #$00
        self._write(mpu.memory, 0x0000, (0x69, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_adc_bcd_on_immediate_6f_plus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x6f
        # $0000 ADC #$00
        self._write(mpu.memory, 0x0000, (0x69, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x76, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_adc_bcd_on_immediate_9c_plus_9d(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x9c
        # $0000 ADC #$9d
        # $0002 ADC #$9d
        self._write(mpu.memory, 0x0000, (0x69, 0x9d))
        self._write(mpu.memory, 0x0002, (0x69, 0x9d))
        mpu.step()
        self.assertEqual(0x9f, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        mpu.step()
        self.assertEqual(0x0004, mpu.pc)
        self.assertEqual(0x93, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ADC Absolute, X-Indexed

    def test_adc_bcd_off_abs_x_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_abs_x_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0xFE
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0xff
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0xff
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_x_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x40
        mpu.x = 0x03
        # $0000 ADC $C000,X
        self._write(mpu.memory, 0x0000, (0x7D, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.x] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Absolute, Y-Indexed

    def test_adc_bcd_off_abs_y_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_abs_y_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0xFE
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_abs_y_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x40
        mpu.y = 0x03
        # $0000 ADC $C000,Y
        self._write(mpu.memory, 0x0000, (0x79, 0x00, 0xC0))
        mpu.memory[0xC000 + mpu.y] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Zero Page, X-Indexed

    def test_adc_bcd_off_zp_x_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_x_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_zp_x_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFE
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_x_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_zp_x_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_x_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_x_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_x_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xff
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_zp_x_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x40
        mpu.x = 0x03
        # $0000 ADC $0010,X
        self._write(mpu.memory, 0x0000, (0x75, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Indirect, Indexed (X)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFE
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_ind_indexed_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x40
        mpu.x = 0x03
        # $0000 ADC ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x61, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ADC Indexed, Indirect (Y)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_accumulator_zeroes(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_carry_set_in_accumulator_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertNotEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_no_carry_clear_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xFE
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_carry_clear_in_carry_set_out(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_clr_no_carry_01_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x01
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_7f_plus_01(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x7f
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_no_carry_80_plus_ff(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.a = 0x80
        mpu.y = 0x03
        # $0000 $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x7f, mpu.a)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_adc_bcd_off_indexed_ind_overflow_set_on_40_plus_40(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.a = 0x40
        mpu.y = 0x03
        # $0000 ADC ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x71, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND (Absolute)

    def test_and_absolute_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND $ABCD
        self._write(mpu.memory, 0x0000, (0x2D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_absolute_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND $ABCD
        self._write(mpu.memory, 0x0000, (0x2D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xAA
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND (Absolute)

    def test_and_zp_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND $0010
        self._write(mpu.memory, 0x0000, (0x25, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_zp_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND $0010
        self._write(mpu.memory, 0x0000, (0x25, 0x10))
        mpu.memory[0x0010] = 0xAA
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND (Immediate)

    def test_and_immediate_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND #$00
        self._write(mpu.memory, 0x0000, (0x29, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_immediate_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 AND #$AA
        self._write(mpu.memory, 0x0000, (0x29, 0xAA))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND (Absolute, X-Indexed)

    def test_and_abs_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3d, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_abs_x_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3d, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0xAA
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND (Absolute, Y-Indexed)

    def test_and_abs_y_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x39, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_abs_y_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 AND $ABCD,X
        self._write(mpu.memory, 0x0000, (0x39, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xAA
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Indirect, Indexed (X)

    def test_and_ind_indexed_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 AND ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x21, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_ind_indexed_x_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 AND ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x21, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xAA
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Indexed, Indirect (Y)

    def test_and_indexed_ind_y_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x31, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_indexed_ind_y_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 AND ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x31, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xAA
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # AND Zero Page, X-Indexed

    def test_and_zp_x_all_zeros_setting_zero_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 AND $0010,X
        self._write(mpu.memory, 0x0000, (0x35, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_and_zp_x_all_zeros_and_ones_setting_negative_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 AND $0010,X
        self._write(mpu.memory, 0x0000, (0x35, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xAA
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ASL Accumulator

    def test_asl_accumulator_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 ASL A
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_accumulator_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x40
        # $0000 ASL A
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_accumulator_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0x7F
        # $0000 ASL A
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFE, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 ASL A
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFE, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_asl_accumulator_80_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x80
        mpu.p &= ~(mpu.ZERO)
        # $0000 ASL A
        mpu.memory[0x0000] = 0x0A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # ASL Absolute

    def test_asl_absolute_sets_z_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_absolute_sets_n_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $ABCD
        self._write(mpu.memory, 0x0000, (0x0E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Zero Page

    def test_asl_zp_sets_z_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_zp_sets_n_flag(self):
        mpu = self._make_mpu()
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        mpu.memory[0x0010] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_zp_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        mpu.memory[0x0010] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_zp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        # $0000 ASL $0010
        self._write(mpu.memory, 0x0000, (0x06, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Absolute, X-Indexed

    def test_asl_abs_x_indexed_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_abs_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xAA
        mpu.x = 0x03
        # $0000 ASL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ASL Zero Page, X-Indexed

    def test_asl_zp_x_indexed_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_asl_zp_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_asl_zp_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.a = 0xAA
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_asl_zp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.a = 0xAA
        # $0000 ASL $0010,X
        self._write(mpu.memory, 0x0000, (0x16, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xAA, mpu.a)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # BCC

    def test_bcc_carry_clear_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 BCC +6
        self._write(mpu.memory, 0x0000, (0x90, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bcc_carry_clear_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF + 1)  # two's complement of 6
        # $0000 BCC -6
        self._write(mpu.memory, 0x0050, (0x90, rel))
        mpu.step()
        self.assertEqual(0x0052 + rel, mpu.pc)

    def test_bcc_carry_set_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 BCC +6
        self._write(mpu.memory, 0x0000, (0x90, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BCS

    def test_bcs_carry_set_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 BCS +6
        self._write(mpu.memory, 0x0000, (0xB0, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bcs_carry_set_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF + 1)  # two's complement of 6
        # $0000 BCS -6
        self._write(mpu.memory, 0x0050, (0xB0, rel))
        mpu.step()
        self.assertEqual(0x0052 + rel, mpu.pc)

    def test_bcs_carry_clear_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 BCS +6
        self._write(mpu.memory, 0x0000, (0xB0, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BEQ

    def test_beq_zero_set_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BEQ +6
        self._write(mpu.memory, 0x0000, (0xF0, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_beq_zero_set_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF + 1)  # two's complement of 6
        # $0000 BEQ -6
        self._write(mpu.memory, 0x0050, (0xF0, rel))
        mpu.step()
        self.assertEqual(0x0052 + rel, mpu.pc)

    def test_beq_zero_clear_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BEQ +6
        self._write(mpu.memory, 0x0000, (0xF0, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BIT (Absolute)

    def test_bit_abs_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_bit_abs_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_bit_abs_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_bit_abs_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_bit_abs_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])

    def test_bit_abs_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.memory[0xFEED] = 0x01
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0xFEED])

    def test_bit_abs_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT $FEED
        self._write(mpu.memory, 0x0000, (0x2C, 0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0xFEED])

    # BIT (Zero Page)

    def test_bit_zp_copies_bit_7_of_memory_to_n_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_bit_zp_copies_bit_7_of_memory_to_n_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_bit_zp_copies_bit_6_of_memory_to_v_flag_when_0(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(mpu.OVERFLOW, mpu.p & mpu.OVERFLOW)

    def test_bit_zp_copies_bit_6_of_memory_to_v_flag_when_1(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.a = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    def test_bit_zp_stores_result_of_and_in_z_preserves_a_when_1(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.ZERO
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010])

    def test_bit_zp_stores_result_of_and_when_nonzero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        mpu.memory[0x0010] = 0x01
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(0, mpu.p & mpu.ZERO)  # result of AND is non-zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x01, mpu.memory[0x0010])

    def test_bit_zp_stores_result_of_and_when_zero_in_z_preserves_a(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BIT $0010
        self._write(mpu.memory, 0x0000, (0x24, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(3, mpu.processorCycles)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)  # result of AND is zero
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x00, mpu.memory[0x0010])

    # BMI

    def test_bmi_negative_set_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BMI +06
        self._write(mpu.memory, 0x0000, (0x30, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bmi_negative_set_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        mpu.pc = 0x0050
        # $0000 BMI -6
        rel = (0x06 ^ 0xFF + 1)  # two's complement of 6
        self._write(mpu.memory, 0x0050, (0x30, rel))
        mpu.step()
        self.assertEqual(0x0052 + rel, mpu.pc)

    def test_bmi_negative_clear_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BEQ +6
        self._write(mpu.memory, 0x0000, (0x30, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BNE

    def test_bne_zero_clear_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        # $0000 BNE +6
        self._write(mpu.memory, 0x0000, (0xD0, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bne_zero_clear_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.pc = 0x0050
        # $0050 BNE -6
        rel = (0x06 ^ 0xFF + 1)  # two's complement of 6
        self._write(mpu.memory, 0x0050, (0xD0, rel))
        mpu.step()
        self.assertEqual(0x0052 + rel, mpu.pc)

    def test_bne_zero_set_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.ZERO
        # $0000 BNE +6
        self._write(mpu.memory, 0x0000, (0xD0, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BPL

    def test_bpl_negative_clear_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        # $0000 BPL +06
        self._write(mpu.memory, 0x0000, (0x10, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bpl_negative_clear_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.pc = 0x0050
        # $0050 BPL -6
        rel = (0x06 ^ 0xFF + 1)  # two's complement of 6
        self._write(mpu.memory, 0x0050, (0x10, rel))
        mpu.step()
        self.assertEqual(0x0052 + rel, mpu.pc)

    def test_bpl_negative_set_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.NEGATIVE
        # $0000 BPL +6
        self._write(mpu.memory, 0x0000, (0x10, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BRK

    def test_brk_pushes_pc_plus_2_and_status_then_sets_pc_to_irq_vector(self):
        mpu = self._make_mpu()
        mpu.p = mpu.UNUSED
        self._write(mpu.memory, 0xFFFE, (0xCD, 0xAB))
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

        self.assertEqual(0xC0, mpu.memory[0x1FF])  # PCH
        self.assertEqual(0x02, mpu.memory[0x1FE])  # PCL
        self.assertEqual(mpu.BREAK | mpu.UNUSED, mpu.memory[0x1FD])  # Status
        self.assertEqual(0xFC, mpu.sp)

        self.assertEqual(mpu.BREAK | mpu.UNUSED | mpu.INTERRUPT, mpu.p)

    # BVC

    def test_bvc_overflow_clear_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BVC +6
        self._write(mpu.memory, 0x0000, (0x50, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bvc_overflow_clear_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF + 1)  # two's complement of 6
        # $0050 BVC -6
        self._write(mpu.memory, 0x0050, (0x50, rel))
        mpu.step()
        self.assertEqual(0x0052 + rel, mpu.pc)

    def test_bvc_overflow_set_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BVC +6
        self._write(mpu.memory, 0x0000, (0x50, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # BVS

    def test_bvs_overflow_set_branches_relative_forward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 BVS +6
        self._write(mpu.memory, 0x0000, (0x70, 0x06))
        mpu.step()
        self.assertEqual(0x0002 + 0x06, mpu.pc)

    def test_bvs_overflow_set_branches_relative_backward(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        mpu.pc = 0x0050
        rel = (0x06 ^ 0xFF + 1)  # two's complement of 6
        # $0050 BVS -6
        self._write(mpu.memory, 0x0050, (0x70, rel))
        mpu.step()
        self.assertEqual(0x0052 + rel, mpu.pc)

    def test_bvs_overflow_clear_does_not_branch(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.OVERFLOW)
        # $0000 BVS +6
        self._write(mpu.memory, 0x0000, (0x70, 0x06))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)

    # CLC

    def test_clc_clears_carry_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 CLC
        mpu.memory[0x0000] = 0x18
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    # CLD

    def test_cld_clears_decimal_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        # $0000 CLD
        mpu.memory[0x0000] = 0xD8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.DECIMAL)

    # CLI

    def test_cli_clears_interrupt_mask_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.INTERRUPT
        # $0000 CLI
        mpu.memory[0x0000] = 0x58
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.INTERRUPT)

    # CLV

    def test_clv_clears_overflow_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.OVERFLOW
        # $0000 CLV
        mpu.memory[0x0000] = 0xB8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)

    # DEC Absolute

    def test_dec_abs_decrements_memory(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD
        self._write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x10
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0F, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dec_abs_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD
        self._write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dec_abs_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD
        self._write(mpu.memory, 0x0000, (0xCE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEC Zero Page

    def test_dec_zp_decrements_memory(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010
        self._write(mpu.memory, 0x0000, (0xC6, 0x10))
        mpu.memory[0x0010] = 0x10
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0F, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dec_zp_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010
        self._write(mpu.memory, 0x0000, (0xC6, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dec_zp_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010
        self._write(mpu.memory, 0x0000, (0xC6, 0x10))
        mpu.memory[0x0010] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEC Absolute, X-Indexed

    def test_dec_abs_x_decrements_memory(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD,X
        self._write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
        mpu.x = 0x03
        mpu.memory[0xABCD + mpu.x] = 0x10
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0F, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dec_abs_x_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD,X
        self._write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dec_abs_x_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC 0xABCD,X
        self._write(mpu.memory, 0x0000, (0xDE, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEC Zero Page, X-Indexed

    def test_dec_zp_x_decrements_memory(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010,X
        self._write(mpu.memory, 0x0000, (0xD6, 0x10))
        mpu.x = 0x03
        mpu.memory[0x0010 + mpu.x] = 0x10
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0F, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dec_zp_x_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010,X
        self._write(mpu.memory, 0x0000, (0xD6, 0x10))
        mpu.x = 0x03
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dec_zp_x_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        # $0000 DEC 0x0010,X
        self._write(mpu.memory, 0x0000, (0xD6, 0x10))
        mpu.x = 0x03
        mpu.memory[0x0010 + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEX

    def test_dex_decrements_x(self):
        mpu = self._make_mpu()
        mpu.x = 0x10
        # $0000 DEX
        mpu.memory[0x0000] = 0xCA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0F, mpu.x)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dex_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        # $0000 DEX
        mpu.memory[0x0000] = 0xCA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFF, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dex_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x01
        # $0000 DEX
        mpu.memory[0x0000] = 0xCA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # DEY

    def test_dey_decrements_y(self):
        mpu = self._make_mpu()
        mpu.y = 0x10
        # $0000 DEY
        mpu.memory[0x0000] = 0x88
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0F, mpu.y)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_dey_below_00_rolls_over_and_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 DEY
        mpu.memory[0x0000] = 0x88
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFF, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_dey_sets_zero_flag_when_decrementing_to_zero(self):
        mpu = self._make_mpu()
        mpu.y = 0x01
        # $0000 DEY
        mpu.memory[0x0000] = 0x88
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # EOR Absolute

    def test_eor_absolute_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        self._write(mpu.memory, 0x0000, (0x4D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_absolute_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0x4D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Zero Page

    def test_eor_zp_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        self._write(mpu.memory, 0x0000, (0x45, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_zp_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0x45, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Immediate

    def test_eor_immediate_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        self._write(mpu.memory, 0x0000, (0x49, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_immediate_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        self._write(mpu.memory, 0x0000, (0x49, 0xFF))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Absolute, X-Indexed

    def test_eor_abs_x_indexed_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x5D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_abs_x_indexed_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x5D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Absolute, Y-Indexed

    def test_eor_abs_y_indexed_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x59, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_abs_y_indexed_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x59, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Indirect, Indexed (X)

    def test_eor_ind_indexed_x_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_ind_indexed_x_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x41, 0x10))  # => EOR ($0010,X)
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))  # => Vector to $ABCD
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Indexed, Indirect (Y)

    def test_eor_indexed_ind_y_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_indexed_ind_y_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        self._write(mpu.memory, 0x0000, (0x51, 0x10))  # => EOR ($0010),Y
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))  # => Vector to $ABCD
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # EOR Zero Page, X-Indexed

    def test_eor_zp_x_indexed_flips_bits_over_setting_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x55, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_eor_zp_x_indexed_flips_bits_over_setting_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x55, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # INC Absolute

    def test_inc_abs_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x09
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0A, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xEE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Zero Page

    def test_inc_zp_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        mpu.memory[0x0010] = 0x09
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0A, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_zp_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_zp_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xE6, 0x10))
        mpu.memory[0x0010] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Absolute, X-Indexed

    def test_inc_abs_x_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        mpu.memory[0xABCD + mpu.x] = 0x09
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x0A, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_x_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_abs_x_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xFE, 0xCD, 0xAB))
        mpu.x = 0x03
        mpu.memory[0xABCD + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INC Zero Page, X-Indexed

    def test_inc_zp_x_increments_memory(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        mpu.x = 0x03
        mpu.memory[0x0010 + mpu.x] = 0x09
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0A, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_zp_x_increments_memory_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inc_zp_x_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        self._write(mpu.memory, 0x0000, (0xF6, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INX

    def test_inx_increments_x(self):
        mpu = self._make_mpu()
        mpu.x = 0x09
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0A, mpu.x)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_inx_above_FF_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_inx_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.x = 0x7f
        mpu.memory[0x0000] = 0xE8  # => INX
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # INY

    def test_iny_increments_y(self):
        mpu = self._make_mpu()
        mpu.y = 0x09
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x0A, mpu.y)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_iny_above_FF_rolls_over_and_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_iny_sets_negative_flag_when_incrementing_above_7F(self):
        mpu = self._make_mpu()
        mpu.y = 0x7f
        mpu.memory[0x0000] = 0xC8  # => INY
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    # JMP Absolute

    def test_jmp_abs_jumps_to_absolute_address(self):
        mpu = self._make_mpu()
        # $0000 JMP $ABCD
        self._write(mpu.memory, 0x0000, (0x4C, 0xCD, 0xAB))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

    # JMP Indirect

    def test_jmp_ind_jumps_to_indirect_address(self):
        mpu = self._make_mpu()
        # $0000 JMP ($ABCD)
        self._write(mpu.memory, 0x0000, (0x6C, 0x00, 0x02))
        self._write(mpu.memory, 0x0200, (0xCD, 0xAB))
        mpu.step()
        self.assertEqual(0xABCD, mpu.pc)

    # JSR

    def test_jsr_pushes_pc_plus_2_and_sets_pc(self):
        mpu = self._make_mpu()
        # $C000 JSR $FFD2
        self._write(mpu.memory, 0xC000, (0x20, 0xD2, 0xFF))
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(0xFFD2, mpu.pc)
        self.assertEqual(0xFD,   mpu.sp)
        self.assertEqual(0xC0,   mpu.memory[0x01FF])  # PCH
        self.assertEqual(0x02,   mpu.memory[0x01FE])  # PCL+2

    # LDA Absolute

    def test_lda_absolute_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA $ABCD
        self._write(mpu.memory, 0x0000, (0xAD, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_absolute_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 LDA $ABCD
        self._write(mpu.memory, 0x0000, (0xAD, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Zero Page

    def test_lda_zp_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA $0010
        self._write(mpu.memory, 0x0000, (0xA5, 0x10))
        mpu.memory[0x0010] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_zp_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 LDA $0010
        self._write(mpu.memory, 0x0000, (0xA5, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Immediate

    def test_lda_immediate_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        # $0000 LDA #$80
        self._write(mpu.memory, 0x0000, (0xA9, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_immediate_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        # $0000 LDA #$00
        self._write(mpu.memory, 0x0000, (0xA9, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Absolute, X-Indexed

    def test_lda_abs_x_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBD, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_abs_x_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 LDA $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBD, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lda_abs_x_indexed_does_not_page_wrap(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.x = 0xFF
        # $0000 LDA $0080,X
        self._write(mpu.memory, 0x0000, (0xBD, 0x80, 0x00))
        mpu.memory[0x0080 + mpu.x] = 0x42
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x42, mpu.a)

    # LDA Absolute, Y-Indexed

    def test_lda_abs_y_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 LDA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xB9, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_abs_y_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 LDA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xB9, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lda_abs_y_indexed_does_not_page_wrap(self):
        mpu = self._make_mpu()
        mpu.a = 0
        mpu.y = 0xFF
        # $0000 LDA $0080,X
        self._write(mpu.memory, 0x0000, (0xB9, 0x80, 0x00))
        mpu.memory[0x0080 + mpu.y] = 0x42
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x42, mpu.a)

    # LDA Indirect, Indexed (X)

    def test_lda_ind_indexed_x_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xA1, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_ind_indexed_x_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xA1, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Indexed, Indirect (Y)

    def test_lda_indexed_ind_y_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB1, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_indexed_ind_y_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 LDA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0xB1, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDA Zero Page, X-Indexed

    def test_lda_zp_x_indexed_loads_a_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 LDA $10,X
        self._write(mpu.memory, 0x0000, (0xB5, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_lda_zp_x_indexed_loads_a_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 LDA $10,X
        self._write(mpu.memory, 0x0000, (0xB5, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Absolute

    def test_ldx_absolute_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        # $0000 LDX $ABCD
        self._write(mpu.memory, 0x0000, (0xAE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_absolute_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        # $0000 LDX $ABCD
        self._write(mpu.memory, 0x0000, (0xAE, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Zero Page

    def test_ldx_zp_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        # $0000 LDX $0010
        self._write(mpu.memory, 0x0000, (0xA6, 0x10))
        mpu.memory[0x0010] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_zp_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        # $0000 LDX $0010
        self._write(mpu.memory, 0x0000, (0xA6, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Immediate

    def test_ldx_immediate_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        # $0000 LDX #$80
        self._write(mpu.memory, 0x0000, (0xA2, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_immediate_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        # $0000 LDX #$00
        self._write(mpu.memory, 0x0000, (0xA2, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Absolute, Y-Indexed

    def test_ldx_abs_y_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        mpu.y = 0x03
        # $0000 LDX $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xBE, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_abs_y_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        mpu.y = 0x03
        # $0000 LDX $ABCD,Y
        self._write(mpu.memory, 0x0000, (0xBE, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDX Zero Page, Y-Indexed

    def test_ldx_zp_y_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x00
        mpu.y = 0x03
        # $0000 LDX $0010,Y
        self._write(mpu.memory, 0x0000, (0xB6, 0x10))
        mpu.memory[0x0010 + mpu.y] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldx_zp_y_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0xFF
        mpu.y = 0x03
        # $0000 LDX $0010,Y
        self._write(mpu.memory, 0x0000, (0xB6, 0x10))
        mpu.memory[0x0010 + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Absolute

    def test_ldy_absolute_loads_y_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 LDY $ABCD
        self._write(mpu.memory, 0x0000, (0xAC, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_absolute_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        # $0000 LDY $ABCD
        self._write(mpu.memory, 0x0000, (0xAC, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Zero Page

    def test_ldy_zp_loads_y_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 LDY $0010
        self._write(mpu.memory, 0x0000, (0xA4, 0x10))
        mpu.memory[0x0010] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_zp_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        # $0000 LDY $0010
        self._write(mpu.memory, 0x0000, (0xA4, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Immediate

    def test_ldy_immediate_loads_y_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        # $0000 LDY #$80
        self._write(mpu.memory, 0x0000, (0xA0, 0x80))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_immediate_loads_y_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        # $0000 LDY #$00
        self._write(mpu.memory, 0x0000, (0xA0, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Absolute, X-Indexed

    def test_ldy_abs_x_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        mpu.x = 0x03
        # $0000 LDY $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBC, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_abs_x_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        mpu.x = 0x03
        # $0000 LDY $ABCD,X
        self._write(mpu.memory, 0x0000, (0xBC, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LDY Zero Page, X-Indexed

    def test_ldy_zp_x_indexed_loads_x_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0x00
        mpu.x = 0x03
        # $0000 LDY $0010,X
        self._write(mpu.memory, 0x0000, (0xB4, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_ldy_zp_x_indexed_loads_x_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.y = 0xFF
        mpu.x = 0x03
        # $0000 LDY $0010,X
        self._write(mpu.memory, 0x0000, (0xB4, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Accumulator

    def test_lsr_accumulator_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR A
        mpu.memory[0x0000] = (0x4A)
        mpu.a = 0x00
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_accumulator_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        # $0000 LSR A
        mpu.memory[0x0000] = (0x4A)
        mpu.a = 0x01
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_accumulator_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR A
        mpu.memory[0x0000] = (0x4A)
        mpu.a = 0x04
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Absolute

    def test_lsr_absolute_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_absolute_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_absolute_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $ABCD
        self._write(mpu.memory, 0x0000, (0x4E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x04
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Zero Page

    def test_lsr_zp_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_zp_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        mpu.memory[0x0010] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_zp_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $0010
        self._write(mpu.memory, 0x0000, (0x46, 0x10))
        mpu.memory[0x0010] = 0x04
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Absolute, X-Indexed

    def test_lsr_abs_x_indexed_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_abs_x_indexed_sets_c_and_z_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_abs_x_indexed_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 LSR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x5E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x04
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # LSR Zero Page, X-Indexed

    def test_lsr_zp_x_indexed_rotates_in_zero_not_carry(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_zp_x_indexed_sets_carry_and_zero_flags_after_rotation(self):
        mpu = self._make_mpu()
        mpu.p &= ~mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x01
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_lsr_zp_x_indexed_rotates_bits_right(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        mpu.x = 0x03
        # $0000 LSR $0010,X
        self._write(mpu.memory, 0x0000, (0x56, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x04
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x02, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    # NOP

    def test_nop_does_nothing(self):
        mpu = self._make_mpu()
        # $0000 NOP
        mpu.memory[0x0000] = 0xEA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)

    # ORA Absolute

    def test_ora_absolute_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA $ABCD
        self._write(mpu.memory, 0x0000, (0x0D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_absolute_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        # $0000 ORA $ABCD
        self._write(mpu.memory, 0x0000, (0x0D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x82
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Zero Page

    def test_ora_zp_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA $0010
        self._write(mpu.memory, 0x0000, (0x05, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_zp_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        # $0000 ORA $0010
        self._write(mpu.memory, 0x0000, (0x05, 0x10))
        mpu.memory[0x0010] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Immediate

    def test_ora_immediate_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 ORA #$00
        self._write(mpu.memory, 0x0000, (0x09, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_immediate_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        # $0000 ORA #$82
        self._write(mpu.memory, 0x0000, (0x09, 0x82))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Absolute, X

    def test_ora_abs_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ORA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_abs_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.x = 0x03
        # $0000 ORA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x1D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x82
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Absolute, Y

    def test_ora_abs_y_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ORA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x19, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_abs_y_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.y = 0x03
        # $0000 ORA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x19, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x82
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Indirect, Indexed (X)

    def test_ora_ind_indexed_x_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ORA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x01, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_ind_indexed_x_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.x = 0x03
        # $0000 ORA ($0010,X)
        # $0013 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x01, 0x10))
        self._write(mpu.memory, 0x0013, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Indexed, Indirect (Y)

    def test_ora_indexed_ind_y_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 ORA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x11, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_indexed_ind_y_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.y = 0x03
        # $0000 ORA ($0010),Y
        # $0010 Vector to $ABCD
        self._write(mpu.memory, 0x0000, (0x11, 0x10))
        self._write(mpu.memory, 0x0010, (0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # ORA Zero Page, X

    def test_ora_zp_x_indexed_zeroes_or_zeros_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 ORA $0010,X
        self._write(mpu.memory, 0x0000, (0x15, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_ora_zp_x_indexed_turns_bits_on_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x03
        mpu.x = 0x03
        # $0000 ORA $0010,X
        self._write(mpu.memory, 0x0000, (0x15, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x82
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x83, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # PHA

    def test_pha_pushes_a_and_updates_sp(self):
        mpu = self._make_mpu()
        mpu.a = 0xAB
        # $0000 PHA
        mpu.memory[0x0000] = 0x48
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.memory[0x01FF])
        self.assertEqual(0xFE, mpu.sp)

    # PHP

    def test_php_pushes_processor_status_and_updates_sp(self):
        for flags in range(0x100):
            mpu = self._make_mpu()
            mpu.p = flags | mpu.BREAK | mpu.UNUSED
            # $0000 PHP
            mpu.memory[0x0000] = 0x08
            mpu.step()
            self.assertEqual(0x0001, mpu.pc)
            self.assertEqual((flags | mpu.BREAK | mpu.UNUSED),
                             mpu.memory[0x1FF])
            self.assertEqual(0xFE, mpu.sp)

    # PLA

    def test_pla_pulls_top_byte_from_stack_into_a_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLA
        mpu.memory[0x0000] = 0x68
        mpu.memory[0x01FF] = 0xAB
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB,   mpu.a)
        self.assertEqual(0xFF,   mpu.sp)

    # PLP

    def test_plp_pulls_top_byte_from_stack_into_flags_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 PLP
        mpu.memory[0x0000] = 0x28
        mpu.memory[0x01FF] = 0xBA  # must have BREAK and UNUSED set
        mpu.sp = 0xFE
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xBA,   mpu.p)
        self.assertEqual(0xFF,   mpu.sp)

    # ROL Accumulator

    def test_rol_accumulator_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_accumulator_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x80
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_accumulator_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_accumulator_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x40
        mpu.p |= mpu.CARRY
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x81, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_accumulator_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0x7F
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFE, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0xFF
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL A
        mpu.memory[0x0000] = 0x2A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xFE, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Absolute

    def test_rol_absolute_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_absolute_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD
        self._write(mpu.memory, 0x0000, (0x2E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Zero Page

    def test_rol_zp_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_zp_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_zp_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_zp_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_zp_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_zp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010
        self._write(mpu.memory, 0x0000, (0x26, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Absolute, X-Indexed

    def test_rol_abs_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.x = 0x03
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x03
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_abs_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x40
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $ABCD,X
        self._write(mpu.memory, 0x0000, (0x3E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROL Zero Page, X-Indexed

    def test_rol_zp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_zp_x_indexed_80_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x03
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.memory[0x0010 + mpu.x] = 0x80
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_zp_x_indexed_zero_and_carry_one_clears_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        # $0000 ROL $0010,X
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x01, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_rol_zp_x_indexed_sets_n_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x40
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    def test_rol_zp_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x7F
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_rol_zp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROL $0010,X
        self._write(mpu.memory, 0x0000, (0x36, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFE, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Accumulator

    def test_ror_accumulator_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_accumulator_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.p |= mpu.CARRY
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_accumulator_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.a = 0x02
        mpu.p |= mpu.CARRY
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x81, mpu.a)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_accumulator_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.a = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR A
        mpu.memory[0x0000] = 0x6A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x81, mpu.a)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Absolute

    def test_ror_absolute_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_absolute_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x02
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_absolute_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD
        self._write(mpu.memory, 0x0000, (0x6E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x03
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Zero Page

    def test_ror_zp_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_zp_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_zp_zero_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        mpu.memory[0x0010] = 0x02
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_zp_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010
        self._write(mpu.memory, 0x0000, (0x66, 0x10))
        mpu.memory[0x0010] = 0x03
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Absolute, X-Indexed

    def test_ror_abs_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_abs_x_indexed_z_and_c_1_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_abs_x_indexed_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x02
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_abs_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $ABCD,X
        self._write(mpu.memory, 0x0000, (0x7E, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x03
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # ROR Zero Page, X-Indexed

    def test_ror_zp_x_indexed_zero_and_carry_zero_sets_z_flag(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p &= ~(mpu.CARRY)
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_ror_zp_x_indexed_zero_and_carry_one_rotates_in_sets_n_flags(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x80, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_ror_zp_x_indexed_zero_absolute_shifts_out_zero(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x02
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_ror_zp_x_indexed_shifts_out_one(self):
        mpu = self._make_mpu()
        mpu.x = 0x03
        mpu.p |= mpu.CARRY
        # $0000 ROR $0010,X
        self._write(mpu.memory, 0x0000, (0x76, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x03
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x81, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # RTI

    def test_rti_restores_status_and_pc_and_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTI
        mpu.memory[0x0000] = 0x40
        self._write(mpu.memory, 0x01FD, (0xFC, 0x03, 0xC0))  # Status, PCL, PCH
        mpu.sp = 0xFC

        mpu.step()
        self.assertEqual(0xC003, mpu.pc)
        self.assertEqual(0xFC,   mpu.p)
        self.assertEqual(0xFF,   mpu.sp)

    def test_rti_forces_break_and_unused_flags_high(self):
        mpu = self._make_mpu()
        # $0000 RTI
        mpu.memory[0x0000] = 0x40
        self._write(mpu.memory, 0x01FD, (0x00, 0x03, 0xC0))  # Status, PCL, PCH
        mpu.sp = 0xFC

        mpu.step()
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(mpu.UNUSED, mpu.p & mpu.UNUSED)

    # RTS

    def test_rts_restores_pc_and_increments_then_updates_sp(self):
        mpu = self._make_mpu()
        # $0000 RTS
        mpu.memory[0x0000] = 0x60
        self._write(mpu.memory, 0x01FE, (0x03, 0xC0))  # PCL, PCH
        mpu.pc = 0x0000
        mpu.sp = 0xFD

        mpu.step()
        self.assertEqual(0xC004, mpu.pc)
        self.assertEqual(0xFF,   mpu.sp)

    def test_rts_wraps_around_top_of_memory(self):
        mpu = self._make_mpu()
        # $1000 RTS
        mpu.memory[0x1000] = 0x60
        self._write(mpu.memory, 0x01FE, (0xFF, 0xFF))  # PCL, PCH
        mpu.pc = 0x1000
        mpu.sp = 0xFD

        mpu.step()
        self.assertEqual(0x0000, mpu.pc)
        self.assertEqual(0xFF,   mpu.sp)

    # SBC Absolute

    def test_sbc_abs_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $ABCD
        self._write(mpu.memory, 0x0000, (0xED, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x02
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Zero Page

    def test_sbc_zp_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        mpu.memory[0x0010] = 0x01
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # => SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # => SBC $10
        self._write(mpu.memory, 0x0000, (0xE5, 0x10))
        mpu.memory[0x0010] = 0x02
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Immediate

    def test_sbc_imm_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xE9, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC #$01
        self._write(mpu.memory, 0x0000, (0xE9, 0x01))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xE9, 0x00))
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_imm_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC #$02
        self._write(mpu.memory, 0x0000, (0xE9, 0x02))
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    def test_sbc_bcd_on_immediate_0a_minus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x0a
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x0a, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_sbc_bcd_on_immediate_9a_minus_00_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.CARRY
        mpu.a = 0x9a
        #$0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x00))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x9a, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    def test_sbc_bcd_on_immediate_00_minus_01_carry_set(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.p |= mpu.OVERFLOW
        mpu.p |= mpu.ZERO
        mpu.p |= mpu.CARRY
        mpu.a = 0x00
        # => $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x01))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x99, mpu.a)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(0, mpu.p & mpu.CARRY)

    def test_sbc_bcd_on_immediate_20_minus_0a_carry_unset(self):
        mpu = self._make_mpu()
        mpu.p |= mpu.DECIMAL
        mpu.a = 0x20
        # $0000 SBC #$00
        self._write(mpu.memory, 0x0000, (0xe9, 0x0a))
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x1f, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.OVERFLOW)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # SBC Absolute, X-Indexed

    def test_sbc_abs_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        mpu.memory[0xFEED] = 0x01
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $FEE0,X
        self._write(mpu.memory, 0x0000, (0xFD, 0xE0, 0xFE))
        mpu.x = 0x0D
        mpu.memory[0xFEED] = 0x02
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Absolute, Y-Indexed

    def test_sbc_abs_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        mpu.memory[0xFEED] = 0x01
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_abs_y_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $FEE0,Y
        self._write(mpu.memory, 0x0000, (0xF9, 0xE0, 0xFE))
        mpu.y = 0x0D
        mpu.memory[0xFEED] = 0x02
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Indirect, Indexed (X)

    def test_sbc_ind_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        mpu.memory[0xFEED] = 0x01
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xE1, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.x = 0x03
        mpu.memory[0xFEED] = 0x02
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Indexed, Indirect (Y)

    def test_sbc_ind_y_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0x01
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_ind_y_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC ($10),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0xF1, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0x02
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SBC Zero Page, X-Indexed

    def test_sbc_zp_x_all_zeros_and_no_borrow_is_zero(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x00
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        mpu.memory[0x001D] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_x_downto_zero_no_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p |= mpu.CARRY  # borrow = 0
        mpu.a = 0x01
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        mpu.memory[0x001D] = 0x01
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_x_downto_zero_with_borrow_sets_z_clears_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x01
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        mpu.memory[0x001D] = 0x00
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(mpu.CARRY, mpu.CARRY)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    def test_sbc_zp_x_downto_four_with_borrow_clears_z_n(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        mpu.p &= ~(mpu.CARRY)  # borrow = 1
        mpu.a = 0x07
        # $0000 SBC $10,X
        self._write(mpu.memory, 0x0000, (0xF5, 0x10))
        mpu.x = 0x0D
        mpu.memory[0x001D] = 0x02
        mpu.step()
        self.assertEqual(0x04, mpu.a)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)
        self.assertEqual(0, mpu.p & mpu.ZERO)
        self.assertEqual(mpu.CARRY, mpu.CARRY)

    # SEC

    def test_sec_sets_carry_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.CARRY)
        # $0000 SEC
        mpu.memory[0x0000] = 0x038
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(mpu.CARRY, mpu.p & mpu.CARRY)

    # SED

    def test_sed_sets_decimal_mode_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.DECIMAL)
        # $0000 SED
        mpu.memory[0x0000] = 0xF8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(mpu.DECIMAL, mpu.p & mpu.DECIMAL)

    # SEI

    def test_sei_sets_interrupt_disable_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.INTERRUPT)
        # $0000 SEI
        mpu.memory[0x0000] = 0x78
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(mpu.INTERRUPT, mpu.p & mpu.INTERRUPT)

    # STA Absolute

    def test_sta_absolute_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        # $0000 STA $ABCD
        self._write(mpu.memory, 0x0000, (0x8D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_absolute_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA $ABCD
        self._write(mpu.memory, 0x0000, (0x8D, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Zero Page

    def test_sta_zp_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        # $0000 STA $0010
        self._write(mpu.memory, 0x0000, (0x85, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_zp_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        # $0000 STA $0010
        self._write(mpu.memory, 0x0000, (0x85, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Absolute, X-Indexed

    def test_sta_abs_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 STA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x9D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_abs_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 STA $ABCD,X
        self._write(mpu.memory, 0x0000, (0x9D, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.x])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Absolute, Y-Indexed

    def test_sta_abs_y_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 STA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x99, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_abs_y_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 STA $ABCD,Y
        self._write(mpu.memory, 0x0000, (0x99, 0xCD, 0xAB))
        mpu.memory[0xABCD + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD + mpu.y])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Indirect, Indexed (X)

    def test_sta_ind_indexed_x_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 STA ($0010,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x81, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xFEED])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_ind_indexed_x_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 STA ($0010,X)
        # $0013 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x81, 0x10))
        self._write(mpu.memory, 0x0013, (0xED, 0xFE))
        mpu.memory[0xFEED] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xFEED])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Indexed, Indirect (Y)

    def test_sta_indexed_ind_y_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.y = 0x03
        # $0000 STA ($0010),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x91, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xFEED + mpu.y])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_indexed_ind_y_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0x03
        # $0000 STA ($0010),Y
        # $0010 Vector to $FEED
        self._write(mpu.memory, 0x0000, (0x91, 0x10))
        self._write(mpu.memory, 0x0010, (0xED, 0xFE))
        mpu.memory[0xFEED + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xFEED + mpu.y])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STA Zero Page, X-Indexed

    def test_sta_zp_x_indexed_stores_a_leaves_a_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.a = 0xFF
        mpu.x = 0x03
        # $0000 STA $0010,X
        self._write(mpu.memory, 0x0000, (0x95, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.a)
        self.assertEqual(flags, mpu.p)

    def test_sta_zp_x_indexed_stores_a_leaves_a_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0x03
        # $0000 STA $0010,X
        self._write(mpu.memory, 0x0000, (0x95, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(flags, mpu.p)

    # STX Absolute

    def test_stx_absolute_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.x = 0xFF
        # $0000 STX $ABCD
        self._write(mpu.memory, 0x0000, (0x8E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_absolute_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.x = 0x00
        # $0000 STX $ABCD
        self._write(mpu.memory, 0x0000, (0x8E, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STX Zero Page

    def test_stx_zp_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.x = 0xFF
        # $0000 STX $0010
        self._write(mpu.memory, 0x0000, (0x86, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_zp_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.x = 0x00
        # $0000 STX $0010
        self._write(mpu.memory, 0x0000, (0x86, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STX Zero Page, Y-Indexed

    def test_stx_zp_y_indexed_stores_x_leaves_x_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.x = 0xFF
        mpu.y = 0x03
        # $0000 STX $0010,Y
        self._write(mpu.memory, 0x0000, (0x96, 0x10))
        mpu.memory[0x0010 + mpu.y] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.y])
        self.assertEqual(0xFF, mpu.x)
        self.assertEqual(flags, mpu.p)

    def test_stx_zp_y_indexed_stores_x_leaves_x_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.x = 0x00
        mpu.y = 0x03
        # $0000 STX $0010,Y
        self._write(mpu.memory, 0x0000, (0x96, 0x10))
        mpu.memory[0x0010 + mpu.y] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.y])
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(flags, mpu.p)

    # STY Absolute

    def test_sty_absolute_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.y = 0xFF
        # $0000 STY $ABCD
        self._write(mpu.memory, 0x0000, (0x8C, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0xABCD])
        self.assertEqual(0xFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_absolute_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.y = 0x00
        # $0000 STY $ABCD
        self._write(mpu.memory, 0x0000, (0x8C, 0xCD, 0xAB))
        mpu.memory[0xABCD] = 0xFF
        mpu.step()
        self.assertEqual(0x0003, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0xABCD])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # STY Zero Page

    def test_sty_zp_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.y = 0xFF
        # $0000 STY $0010
        self._write(mpu.memory, 0x0000, (0x84, 0x10))
        mpu.memory[0x0010] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010])
        self.assertEqual(0xFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_zp_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.y = 0x00
        # $0000 STY $0010
        self._write(mpu.memory, 0x0000, (0x84, 0x10))
        mpu.memory[0x0010] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # STY Zero Page, X-Indexed

    def test_sty_zp_x_indexed_stores_y_leaves_y_and_n_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.NEGATIVE)
        mpu.y = 0xFF
        mpu.x = 0x03
        # $0000 STY $0010,X
        self._write(mpu.memory, 0x0000, (0x94, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0x00
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0xFF, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0xFF, mpu.y)
        self.assertEqual(flags, mpu.p)

    def test_sty_zp_x_indexed_stores_y_leaves_y_and_z_flag_unchanged(self):
        mpu = self._make_mpu()
        mpu.p = flags = 0xFF & ~(mpu.ZERO)
        mpu.y = 0x00
        mpu.x = 0x03
        # $0000 STY $0010,X
        self._write(mpu.memory, 0x0000, (0x94, 0x10))
        mpu.memory[0x0010 + mpu.x] = 0xFF
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x00, mpu.memory[0x0010 + mpu.x])
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(flags, mpu.p)

    # TAX

    def test_tax_transfers_accumulator_into_x(self):
        mpu = self._make_mpu()
        mpu.a = 0xAB
        mpu.x = 0x00
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.x)

    def test_tax_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x80
        mpu.x = 0x00
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tax_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.x = 0xFF
        # $0000 TAX
        mpu.memory[0x0000] = 0xAA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TAY

    def test_tay_transfers_accumulator_into_y(self):
        mpu = self._make_mpu()
        mpu.a = 0xAB
        mpu.y = 0x00
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.y)

    def test_tay_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.a = 0x80
        mpu.y = 0x00
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tay_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.a = 0x00
        mpu.y = 0xFF
        # $0000 TAY
        mpu.memory[0x0000] = 0xA8
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TSX

    def test_tsx_transfers_stack_pointer_into_x(self):
        mpu = self._make_mpu()
        mpu.sp = 0xAB
        mpu.x = 0x00
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.sp)
        self.assertEqual(0xAB, mpu.x)

    def test_tsx_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.sp = 0x80
        mpu.x = 0x00
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.sp)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tsx_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.sp = 0x00
        mpu.y = 0xFF
        # $0000 TSX
        mpu.memory[0x0000] = 0xBA
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TXA

    def test_txa_transfers_x_into_a(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        mpu.a = 0x00
        # $0000 TXA
        mpu.memory[0x0000] = 0x8A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.x)

    def test_txa_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x80
        mpu.a = 0x00
        # $0000 TXA
        mpu.memory[0x0000] = 0x8A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_txa_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x00
        mpu.a = 0xFF
        # $0000 TXA
        mpu.memory[0x0000] = 0x8A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # TXS

    def test_txs_transfers_x_into_stack_pointer(self):
        mpu = self._make_mpu()
        mpu.x = 0xAB
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.sp)
        self.assertEqual(0xAB, mpu.x)

    def test_txs_does_not_set_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.x = 0x80
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.sp)
        self.assertEqual(0x80, mpu.x)
        self.assertEqual(0, mpu.p & mpu.NEGATIVE)

    def test_txs_does_not_set_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.x = 0x00
        # $0000 TXS
        mpu.memory[0x0000] = 0x9A
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x00, mpu.sp)
        self.assertEqual(0x00, mpu.x)
        self.assertEqual(0, mpu.p & mpu.ZERO)

    # TYA

    def test_tya_transfers_y_into_a(self):
        mpu = self._make_mpu()
        mpu.y = 0xAB
        mpu.a = 0x00
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0xAB, mpu.a)
        self.assertEqual(0xAB, mpu.y)

    def test_tya_sets_negative_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.NEGATIVE)
        mpu.y = 0x80
        mpu.a = 0x00
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x0001, mpu.pc)
        self.assertEqual(0x80, mpu.a)
        self.assertEqual(0x80, mpu.y)
        self.assertEqual(mpu.NEGATIVE, mpu.p & mpu.NEGATIVE)

    def test_tya_sets_zero_flag(self):
        mpu = self._make_mpu()
        mpu.p &= ~(mpu.ZERO)
        mpu.y = 0x00
        mpu.a = 0xFF
        # $0000 TYA
        mpu.memory[0x0000] = 0x98
        mpu.step()
        self.assertEqual(0x00, mpu.a)
        self.assertEqual(0x00, mpu.y)
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)
        self.assertEqual(0x0001, mpu.pc)

    def test_decorated_addressing_modes_are_valid(self):
        valid_modes = [x[0] for x in py65.assembler.Assembler.Addressing]
        mpu = self._make_mpu()
        for name, mode in mpu.disassemble:
            self.assertTrue(mode in valid_modes)

    def test_brk_interrupt(self):
        mpu = self._make_mpu()
        mpu.p = 0x00
        self._write(mpu.memory, 0xFFFE, (0x00, 0x04))

        self._write(mpu.memory, 0x0000, (0xA9, 0x01,   # LDA #$01
                                         0x00, 0xEA,   # BRK + skipped byte
                                         0xEA, 0xEA,   # NOP, NOP
                                         0xA9, 0x03))  # LDA #$03

        self._write(mpu.memory, 0x0400, (0xA9, 0x02,   # LDA #$02
                                         0x40))        # RTI

        mpu.step()  # LDA #$01
        self.assertEqual(0x01, mpu.a)
        self.assertEqual(0x0002, mpu.pc)
        mpu.step()  # BRK
        self.assertEqual(0x0400, mpu.pc)
        mpu.step()  # LDA #$02
        self.assertEqual(0x02, mpu.a)
        self.assertEqual(0x0402, mpu.pc)
        mpu.step()  # RTI

        self.assertEqual(0x0004, mpu.pc)
        mpu.step()  # A NOP
        mpu.step()  # The second NOP

        mpu.step()  # LDA #$03
        self.assertEqual(0x03, mpu.a)
        self.assertEqual(0x0008, mpu.pc)

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
        raise NotImplementedError("Target class not specified")


class MPUTests(unittest.TestCase, Common6502Tests):
    """ NMOS 6502 tests """

    def test_repr(self):
        mpu = self._make_mpu()
        self.assertTrue("6502" in repr(mpu))

    # ADC Indirect, Indexed (X)

    def test_adc_ind_indexed_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.p = 0x00
        mpu.a = 0x01
        mpu.x = 0xFF
        # $0000 ADC ($80,X)
        # $007f Vector to $BBBB (read if page wrapped)
        # $017f Vector to $ABCD (read if no page wrap)
        self._write(mpu.memory, 0x0000, (0x61, 0x80))
        self._write(mpu.memory, 0x007f, (0xBB, 0xBB))
        self._write(mpu.memory, 0x017f, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x01
        mpu.memory[0xBBBB] = 0x02
        mpu.step()
        self.assertEqual(0x03, mpu.a)

    # ADC Indexed, Indirect (Y)

    def test_adc_indexed_ind_y_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.pc = 0x1000
        mpu.p = 0
        mpu.a = 0x42
        mpu.y = 0x02
        # $1000 ADC ($FF),Y
        self._write(mpu.memory, 0x1000, (0x71, 0xff))
        # Vector
        mpu.memory[0x00ff] = 0x10 # low byte
        mpu.memory[0x0100] = 0x20 # high byte if no page wrap
        mpu.memory[0x0000] = 0x00 # high byte if page wrapped
        # Data
        mpu.memory[0x2012] = 0x14 # read if no page wrap
        mpu.memory[0x0012] = 0x42 # read if page wrapped
        mpu.step()
        self.assertEqual(0x84, mpu.a)

    # LDA Zero Page, X-Indexed

    def test_lda_zp_x_indexed_page_wraps(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0xFF
        # $0000 LDA $80,X
        self._write(mpu.memory, 0x0000, (0xB5, 0x80))
        mpu.memory[0x007F] = 0x42
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x42, mpu.a)

    # AND Indexed, Indirect (Y)

    def test_and_indexed_ind_y_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.pc = 0x1000
        mpu.a = 0x42
        mpu.y = 0x02
        # $1000 AND ($FF),Y
        self._write(mpu.memory, 0x1000, (0x31, 0xff))
        # Vector
        mpu.memory[0x00ff] = 0x10 # low byte
        mpu.memory[0x0100] = 0x20 # high byte if no page wrap
        mpu.memory[0x0000] = 0x00 # high byte if page wrapped
        # Data
        mpu.memory[0x2012] = 0x00 # read if no page wrap
        mpu.memory[0x0012] = 0xFF # read if page wrapped
        mpu.step()
        self.assertEqual(0x42, mpu.a)

    # BRK

    def test_brk_preserves_decimal_flag_when_it_is_set(self):
        mpu = self._make_mpu()
        mpu.p = mpu.DECIMAL
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(mpu.DECIMAL, mpu.p & mpu.DECIMAL)

    def test_brk_preserves_decimal_flag_when_it_is_clear(self):
        mpu = self._make_mpu()
        mpu.p = 0
        # $C000 BRK
        mpu.memory[0xC000] = 0x00
        mpu.pc = 0xC000
        mpu.step()
        self.assertEqual(mpu.BREAK, mpu.p & mpu.BREAK)
        self.assertEqual(0, mpu.p & mpu.DECIMAL)

    # CMP Indirect, Indexed (X)

    def test_cmp_ind_x_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.p = 0
        mpu.a = 0x42
        mpu.x = 0xFF
        # $0000 CMP ($80,X)
        # $007f Vector to $BBBB (read if page wrapped)
        # $017f Vector to $ABCD (read if no page wrap)
        self._write(mpu.memory, 0x0000, (0xC1, 0x80))
        self._write(mpu.memory, 0x007f, (0xBB, 0xBB))
        self._write(mpu.memory, 0x017f, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.memory[0xBBBB] = 0x42
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # CMP Indexed, Indirect (Y)

    def test_cmp_indexed_ind_y_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.pc = 0x1000
        mpu.p = 0
        mpu.a = 0x42
        mpu.y = 0x02
        # $1000 CMP ($FF),Y
        self._write(mpu.memory, 0x1000, (0xd1, 0xff))
        # Vector
        mpu.memory[0x00ff] = 0x10 # low byte
        mpu.memory[0x0100] = 0x20 # high byte if no page wrap
        mpu.memory[0x0000] = 0x00 # high byte if page wrapped
        # Data
        mpu.memory[0x2012] = 0x14 # read if no page wrap
        mpu.memory[0x0012] = 0x42 # read if page wrapped
        mpu.step()
        self.assertEqual(mpu.ZERO, mpu.p & mpu.ZERO)

    # EOR Indirect, Indexed (X)

    def test_eor_ind_x_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.p = 0
        mpu.a = 0xAA
        mpu.x = 0xFF
        # $0000 EOR ($80,X)
        # $007f Vector to $BBBB (read if page wrapped)
        # $017f Vector to $ABCD (read if no page wrap)
        self._write(mpu.memory, 0x0000, (0x41, 0x80))
        self._write(mpu.memory, 0x007f, (0xBB, 0xBB))
        self._write(mpu.memory, 0x017f, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x00
        mpu.memory[0xBBBB] = 0xFF
        mpu.step()
        self.assertEqual(0x55, mpu.a)

    # EOR Indexed, Indirect (Y)

    def test_eor_indexed_ind_y_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.pc = 0x1000
        mpu.a = 0xAA
        mpu.y = 0x02
        # $1000 EOR ($FF),Y
        self._write(mpu.memory, 0x1000, (0x51, 0xff))
        # Vector
        mpu.memory[0x00ff] = 0x10 # low byte
        mpu.memory[0x0100] = 0x20 # high byte if no page wrap
        mpu.memory[0x0000] = 0x00 # high byte if page wrapped
        # Data
        mpu.memory[0x2012] = 0x00 # read if no page wrap
        mpu.memory[0x0012] = 0xFF # read if page wrapped
        mpu.step()
        self.assertEqual(0x55, mpu.a)

    # LDA Indirect, Indexed (X)

    def test_lda_ind_indexed_x_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0xff
        # $0000 LDA ($80,X)
        # $007f Vector to $BBBB (read if page wrapped)
        # $017f Vector to $ABCD (read if no page wrap)
        self._write(mpu.memory, 0x0000, (0xA1, 0x80))
        self._write(mpu.memory, 0x007f, (0xBB, 0xBB))
        self._write(mpu.memory, 0x017f, (0xCD, 0xAB))
        mpu.memory[0xABCD] = 0x42
        mpu.memory[0xBBBB] = 0xEF
        mpu.step()
        self.assertEqual(0xEF, mpu.a)

    # LDA Indexed, Indirect (Y)

    def test_lda_indexed_ind_y_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.pc = 0x1000
        mpu.a = 0x00
        mpu.y = 0x02
        # $1000 LDA ($FF),Y
        self._write(mpu.memory, 0x1000, (0xb1, 0xff))
        # Vector
        mpu.memory[0x00ff] = 0x10 # low byte
        mpu.memory[0x0100] = 0x20 # high byte if no page wrap
        mpu.memory[0x0000] = 0x00 # high byte if page wrapped
        # Data
        mpu.memory[0x2012] = 0x14 # read if no page wrap
        mpu.memory[0x0012] = 0x42 # read if page wrapped
        mpu.step()
        self.assertEqual(0x42, mpu.a)

    # LDA Zero Page, X-Indexed

    def test_lda_zp_x_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.a = 0x00
        mpu.x = 0xFF
        # $0000 LDA $80,X
        self._write(mpu.memory, 0x0000, (0xB5, 0x80))
        mpu.memory[0x007F] = 0x42
        mpu.step()
        self.assertEqual(0x0002, mpu.pc)
        self.assertEqual(0x42, mpu.a)

    # JMP Indirect

    def test_jmp_jumps_to_address_with_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.memory[0x00ff] = 0
        # $0000 JMP ($00)
        self._write(mpu.memory, 0, (0x6c, 0xff, 0x00))
        mpu.step()
        self.assertEqual(0x6c00, mpu.pc)
        self.assertEqual(5, mpu.processorCycles)

    # ORA Indexed, Indirect (Y)

    def test_ora_indexed_ind_y_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.pc = 0x1000
        mpu.a = 0x00
        mpu.y = 0x02
        # $1000 ORA ($FF),Y
        self._write(mpu.memory, 0x1000, (0x11, 0xff))
        # Vector
        mpu.memory[0x00ff] = 0x10 # low byte
        mpu.memory[0x0100] = 0x20 # high byte if no page wrap
        mpu.memory[0x0000] = 0x00 # high byte if page wrapped
        # Data
        mpu.memory[0x2012] = 0x00 # read if no page wrap
        mpu.memory[0x0012] = 0x42 # read if page wrapped
        mpu.step()
        self.assertEqual(0x42, mpu.a)

    # SBC Indexed, Indirect (Y)

    def test_sbc_indexed_ind_y_has_page_wrap_bug(self):
        mpu = self._make_mpu()
        mpu.pc = 0x1000
        mpu.p = mpu.CARRY
        mpu.a = 0x42
        mpu.y = 0x02
        # $1000 SBC ($FF),Y
        self._write(mpu.memory, 0x1000, (0xf1, 0xff))
        # Vector
        mpu.memory[0x00ff] = 0x10 # low byte
        mpu.memory[0x0100] = 0x20 # high byte if no page wrap
        mpu.memory[0x0000] = 0x00 # high byte if page wrapped
        # Data
        mpu.memory[0x2012] = 0x02 # read if no page wrap
        mpu.memory[0x0012] = 0x03 # read if page wrapped
        mpu.step()
        self.assertEqual(0x3f, mpu.a)

    def _get_target_class(self):
        return py65.devices.mpu6502.MPU


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
