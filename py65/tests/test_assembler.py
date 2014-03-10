import unittest
import sys
from py65.devices.mpu6502 import MPU
from py65.devices.mpu65c02 import MPU as MPU65C02
from py65.devices.mpu65org16 import MPU as MPU65Org16
from py65.assembler import Assembler
from py65.utils.addressing import AddressParser


class AssemblerTests(unittest.TestCase):
    def test_ctor_uses_provided_mpu_and_address_parser(self):
        mpu = MPU()
        address_parser = AddressParser()
        asm = Assembler(mpu, address_parser)
        self.assertTrue(asm._mpu is mpu)
        self.assertTrue(asm._address_parser is address_parser)

    def test_ctor_optionally_creates_address_parser(self):
        mpu = MPU()
        asm = Assembler(mpu)
        self.assertFalse(asm._address_parser is None)

    def test_ctor_uses_bus_width_from_mpu(self):
        asm = Assembler(MPU())
        self.assertEqual(16, asm.addrWidth)
        asm = Assembler(MPU65Org16())
        self.assertEqual(32, asm.addrWidth)

    def test_assemble_bad_syntax_raises_syntaxerror(self):
        self.assertRaises(SyntaxError,
                          self.assemble, 'foo')

    def test_assemble_bad_label_raises_keyerror(self):
        self.assertRaises(KeyError,
                          self.assemble, 'lda foo')

    def test_assemble_tolerates_extra_whitespace(self):
        self.assemble('   lda   #$00   ')  # should not raise

    def test_assemble_bad_number_raises_overflowerror(self):
        self.assertRaises(OverflowError,
                          self.assemble, 'lda #$fff')

    def test_assemble_1_byte_at_top_of_mem_should_not_overflow(self):
        self.assemble('nop', pc=0xFFFF)  # should not raise

    def test_assemble_3_bytes_at_top_of_mem_should_not_overflow(self):
        self.assemble('jmp $1234', pc=0xFFFD)  # should not raise

    def test_assemble_should_overflow_if_over_top_of_mem(self):
        # jmp $1234 requires 3 bytes but there's only 2 at $FFFE-FFFF
        self.assertRaises(OverflowError,
                          self.assemble, "jmp $1234", pc=0xFFFE)

    def test_assembles_00(self):
        self.assertEqual([0x00],
                         self.assemble('BRK'))

    def test_assembles_01(self):
        self.assertEqual([0x01, 0x44],
                         self.assemble('ORA ($44,X)'))

    def dont_test_assembles_02(self):
        pass

    def dont_test_assembles_03(self):
        pass

    def dont_test_assembles_04(self):
        pass

    def test_assembles_04_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x04, 0x42],
                         self.assemble('TSB $42', 0x0000, mpu))

    def test_assembles_05(self):
        self.assertEqual([0x05, 0x44],
                         self.assemble('ORA $44'))

    def test_assembles_06(self):
        self.assertEqual([0x06, 0x44],
                         self.assemble('ASL $44'))

    def test_assembles_07(self):
        self.assertRaises(SyntaxError,
                          self.assemble, "RMB0 $42")

    def test_assembles_07_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x07, 0x42],
                         self.assemble('RMB0 $42', 0x0000, mpu))

    def test_assembles_08(self):
        self.assertEqual([0x08],
                         self.assemble('PHP'))

    def test_assembles_09(self):
        self.assertEqual([0x09, 0x44],
                         self.assemble('ORA #$44'))

    def test_assembles_0a(self):
        self.assertEqual([0x0a],
                         self.assemble('ASL A'))

    def dont_test_assembles_0b(self):
        pass

    def dont_test_assembles_0c(self):
        pass

    def test_assembles_0c_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x0c, 0x34, 0x12],
                         self.assemble('TSB $1234', 0x0000, mpu))

    def test_assembles_0d(self):
        self.assertEqual([0x0d, 0x00, 0x44],
                         self.assemble('ORA $4400'))

    def test_assembles_0e(self):
        self.assertEqual([0x0e, 0x00, 0x44],
                         self.assemble('ASL $4400'))

    def dont_test_assembles_0f(self):
        pass

    def test_assembles_10(self):
        self.assertEqual([0x10, 0x44],
                         self.assemble('BPL $0046'))

    def test_assembles_11(self):
        self.assertEqual([0x11, 0x44],
                         self.assemble('ORA ($44),Y'))

    def dont_test_assembles_12(self):
        pass

    def test_assembles_12_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x12, 0x44],
                         self.assemble('ORA ($44)', 0x0000, mpu))

    def dont_test_assembles_13(self):
        pass

    def dont_test_assembles_14(self):
        pass

    def test_assembles_14_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x14, 0x42],
                         self.assemble('TRB $42', 0x0000, mpu))

    def test_assembles_15(self):
        self.assertEqual([0x15, 0x44],
                         self.assemble('ORA $44,X'))

    def test_assembles_16(self):
        self.assertEqual([0x16, 0x44],
                         self.assemble('ASL $44,X'))

    def dont_test_assembles_17(self):
        pass

    def test_assembles_17_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x17, 0x42],
                         self.assemble('RMB1 $42', 0x0000, mpu))

    def test_assembles_18(self):
        self.assertEqual([0x18],
                         self.assemble('CLC'))

    def test_assembles_19(self):
        self.assertEqual([0x19, 0x00, 0x44],
                         self.assemble('ORA $4400,Y'))

    def dont_test_assembles_1a(self):
        pass

    def test_assembles_1a_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x1a],
                         self.assemble('INC', 0x0000, mpu))

    def dont_test_assembles_1b(self):
        pass

    def test_assembles_1c(self):
        pass

    def test_assembles_1c_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x1c, 0x34, 0x12],
                         self.assemble('TRB $1234', 0x0000, mpu))

    def test_assembles_1d(self):
        self.assertEqual([0x1d, 0x00, 0x44],
                         self.assemble('ORA $4400,X'))

    def test_assembles_1e(self):
        self.assertEqual([0x1e, 0x00, 0x44],
                         self.assemble('ASL $4400,X'))

    def dont_test_assembles_1f(self):
        pass

    def test_assembles_20(self):
        self.assertEqual([0x20, 0x97, 0x55],
                         self.assemble('JSR $5597'))

    def test_assembles_21(self):
        self.assertEqual([0x21, 0x44],
                         self.assemble('AND ($44,X)'))

    def dont_test_assembles_22(self):
        pass

    def dont_test_assembles_23(self):
        pass

    def test_assembles_24(self):
        self.assertEqual([0x24, 0x44],
                         self.assemble('BIT $44'))

    def test_assembles_25(self):
        self.assertEqual([0x25, 0x44],
                         self.assemble('AND $44'))

    def test_assembles_26(self):
        self.assertEqual([0x26, 0x44],
                         self.assemble('ROL $44'))

    def dont_test_assembles_27(self):
        pass

    def test_assembles_27_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x27, 0x42],
                         self.assemble('RMB2 $42', 0x0000, mpu))

    def test_assembles_28(self):
        self.assertEqual([0x28],
                         self.assemble('PLP'))

    def test_assembles_29(self):
        self.assertEqual([0x29, 0x44],
                         self.assemble('AND #$44'))

    def test_assembles_2a(self):
        self.assertEqual([0x2a],
                         self.assemble('ROL A'))

    def dont_test_assembles_2b(self):
        pass

    def test_assembles_2c(self):
        self.assertEqual([0x2c, 0x00, 0x44],
                         self.assemble('BIT $4400'))

    def test_assembles_2d(self):
        self.assertEqual([0x2d, 0x00, 0x44],
                         self.assemble('AND $4400'))

    def test_assembles_2e(self):
        self.assertEqual([0x2e, 0x00, 0x44],
                         self.assemble('ROL $4400'))

    def dont_test_assembles_2f(self):
        pass

    def test_assembles_30(self):
        self.assertEqual([0x30, 0x44],
                         self.assemble('BMI $0046'))

    def test_assembles_31(self):
        self.assertEqual([0x31, 0x44],
                         self.assemble('AND ($44),Y'))

    def dont_test_assembles_32(self):
        pass

    def test_assembles_32_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x32, 0x44],
                         self.assemble('AND ($44)', 0x0000, mpu))

    def dont_test_assembles_33(self):
        pass

    def dont_test_assembles_34(self):
        pass

    def test_assembles_34_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x34, 0x44],
                         self.assemble('BIT $44,X', 0x0000, mpu))

    def test_assembles_35(self):
        self.assertEqual([0x35, 0x44],
                         self.assemble('AND $44,X'))

    def test_assembles_36(self):
        self.assertEqual([0x36, 0x44],
                         self.assemble('ROL $44,X'))

    def dont_test_assembles_37(self):
        pass

    def test_assembles_37_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x37, 0x42],
                         self.assemble('RMB3 $42', 0x0000, mpu))

    def test_assembles_38(self):
        self.assertEqual([0x38],
                         self.assemble('SEC'))

    def test_assembles_39(self):
        self.assertEqual([0x39, 0x00, 0x44],
                         self.assemble('AND $4400,Y'))

    def dont_test_assembles_3a(self):
        pass

    def test_assembles_3a_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x3a],
                         self.assemble('DEC', 0x0000, mpu))

    def dont_test_assembles_3b(self):
        pass

    def dont_test_assembles_3c(self):
        pass

    def test_assembles_3c_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x3c, 0x34, 0x12],
                         self.assemble('BIT $1234,X', 0x0000, mpu))

    def test_assembles_3d(self):
        self.assertEqual([0x3d, 0x00, 0x44],
                         self.assemble('AND $4400,X'))

    def test_assembles_3e(self):
        self.assertEqual([0x3e, 0x00, 0x44],
                         self.assemble('ROL $4400,X'))

    def dont_test_assembles_3f(self):
        pass

    def test_assembles_40(self):
        self.assertEqual([0x40],
                         self.assemble('RTI'))

    def test_assembles_41(self):
        self.assertEqual([0x41, 0x44],
                         self.assemble('EOR ($44,X)'))

    def dont_test_assembles_42(self):
        pass

    def dont_test_assembles_43(self):
        pass

    def dont_test_assembles_44(self):
        pass

    def test_assembles_45(self):
        self.assertEqual([0x45, 0x44],
                         self.assemble('EOR $44'))

    def test_assembles_46(self):
        self.assertEqual([0x46, 0x44],
                         self.assemble('LSR $44'))

    def dont_test_assembles_47(self):
        pass

    def test_assembles_47_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x47, 0x42],
                         self.assemble('RMB4 $42', 0x0000, mpu))

    def test_assembles_48(self):
        self.assertEqual([0x48],
                         self.assemble('PHA'))

    def test_assembles_49(self):
        self.assertEqual([0x49, 0x44],
                         self.assemble('EOR #$44'))

    def test_assembles_4a(self):
        self.assertEqual([0x4a],
                         self.assemble('LSR A'))

    def dont_test_assembles_4b(self):
        pass

    def test_assembles_4c(self):
        self.assertEqual([0x4c, 0x97, 0x55],
                         self.assemble('JMP $5597'))

    def test_assembles_4d(self):
        self.assertEqual([0x4d, 0x00, 0x44],
                         self.assemble('EOR $4400'))

    def test_assembles_4e(self):
        self.assertEqual([0x4e, 0x00, 0x44],
                         self.assemble('LSR $4400'))

    def dont_test_assembles_4f(self):
        pass

    def test_assembles_50(self):
        self.assertEqual([0x50, 0x44],
                         self.assemble('BVC $0046'))

    def test_assembles_51(self):
        self.assertEqual([0x51, 0x44],
                         self.assemble('EOR ($44),Y'))

    def dont_test_assembles_52(self):
        pass

    def test_assembles_52_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x52, 0x44],
                         self.assemble('EOR ($44)', 0x0000, mpu))

    def dont_test_assembles_53(self):
        pass

    def dont_test_assembles_54(self):
        pass

    def test_assembles_55(self):
        self.assertEqual([0x55, 0x44],
                         self.assemble('EOR $44,X'))

    def test_assembles_56(self):
        self.assertEqual([0x56, 0x44],
                         self.assemble('LSR $44,X'))

    def dont_test_assembles_57(self):
        pass

    def test_assembles_57_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x57, 0x42],
                         self.assemble('RMB5 $42', 0x0000, mpu))

    def test_assembles_58(self):
        self.assertEqual([0x58],
                         self.assemble('CLI'))

    def test_assembles_59(self):
        self.assertEqual([0x59, 0x00, 0x44],
                         self.assemble('EOR $4400,Y'))

    def dont_test_assembles_5a(self):
        pass

    def test_assembles_5a_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x5a],
                         self.assemble('PHY', 0x0000, mpu))

    def dont_test_assembles_5b(self):
        pass

    def dont_test_assembles_5c(self):
        pass

    def test_assembles_5d(self):
        self.assertEqual([0x5d, 0x00, 0x44],
                         self.assemble('EOR $4400,X'))

    def test_assembles_5e(self):
        self.assertEqual([0x5e, 0x00, 0x44],
                         self.assemble('LSR $4400,X'))

    def dont_test_assembles_5f(self):
        pass

    def test_assembles_60(self):
        self.assertEqual([0x60],
                         self.assemble('RTS'))

    def test_assembles_61(self):
        self.assertEqual([0x61, 0x44],
                         self.assemble('ADC ($44,X)'))

    def dont_test_assembles_62(self):
        pass

    def dont_test_assembles_63(self):
        pass

    def dont_test_assembles_64(self):
        pass

    def test_assembles_64_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x64],
                         self.assemble('STZ', 0x0000, mpu))

    def test_assembles_65(self):
        self.assertEqual([0x65, 0x44],
                         self.assemble('ADC $44'))

    def test_assembles_66(self):
        self.assertEqual([0x66, 0x44],
                         self.assemble('ROR $44'))

    def dont_test_assembles_67(self):
        pass

    def test_assembles_67_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x67, 0x42],
                         self.assemble('RMB6 $42', 0x0000, mpu))

    def test_assembles_68(self):
        self.assertEqual([0x68],
                         self.assemble('PLA'))

    def test_assembles_69(self):
        self.assertEqual([0x69, 0x44],
                         self.assemble('ADC #$44'))

    def test_assembles_6a(self):
        self.assertEqual([0x6a],
                         self.assemble('ROR A'))

    def dont_test_assembles_6b(self):
        pass

    def test_assembles_6c(self):
        self.assertEqual([0x6c, 0x97, 0x55],
                         self.assemble('JMP ($5597)'))

    def test_assembles_6d(self):
        self.assertEqual([0x6d, 0x00, 0x44],
                         self.assemble('ADC $4400'))

    def test_assembles_6e(self):
        self.assertEqual([0x6e, 0x00, 0x44],
                         self.assemble('ROR $4400'))

    def dont_test_assembles_6f(self):
        pass

    def test_assembles_70(self):
        self.assertEqual([0x70, 0x44],
                         self.assemble('BVS $0046'))

    def test_assembles_71(self):
        self.assertEqual([0x71, 0x44],
                         self.assemble('ADC ($44),Y'))

    def dont_test_assembles_72(self):
        pass

    def test_assembles_72_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x72, 0x44],
                         self.assemble('ADC ($44)', 0x0000, mpu))

    def dont_test_assembles_73(self):
        pass

    def dont_test_assembles_74(self):
        pass

    def test_assembles_74_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x74, 0x44],
                         self.assemble('STZ $44,X', 0x0000, mpu))

    def test_assembles_75(self):
        self.assertEqual([0x75, 0x44],
                         self.assemble('ADC $44,X'))

    def test_assembles_76(self):
        self.assertEqual([0x76, 0x44],
                         self.assemble('ROR $44,X'))

    def test_assembles_77(self):
        pass

    def test_assembles_77_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x77, 0x42],
                         self.assemble('RMB7 $42', 0x0000, mpu))

    def test_assembles_78(self):
        self.assertEqual([0x78],
                         self.assemble('SEI'))

    def test_assembles_79(self):
        self.assertEqual([0x79, 0x00, 0x44],
                         self.assemble('ADC $4400,Y'))

    def dont_test_assembles_7a(self):
        pass

    def test_assembles_7a_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x7a],
                         self.assemble('PLY', 0x0000, mpu))

    def dont_test_assembles_7b(self):
        pass

    def test_assembles_7c_6502(self):
        self.assertRaises(SyntaxError,
                          self.assemble, "JMP ($1234,X)")

    def test_assembles_7c_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x7c, 0x34, 0x12],
                         self.assemble('JMP ($1234,X)', 0x0000, mpu))

    def test_assembles_7d(self):
        self.assertEqual([0x7d, 0x00, 0x44],
                         self.assemble('ADC $4400,X'))

    def test_assembles_7e(self):
        self.assertEqual([0x7e, 0x00, 0x44],
                         self.assemble('ROR $4400,X'))

    def dont_test_assembles_7f(self):
        pass

    def dont_test_assembles_80(self):
        pass

    def test_assembles_80_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x80, 0x44],
                         self.assemble('BRA $0046', 0x0000, mpu))

    def test_assembles_81(self):
        self.assertEqual([0x81, 0x44],
                         self.assemble('STA ($44,X)'))

    def dont_test_assembles_82(self):
        pass

    def dont_test_assembles_83(self):
        pass

    def test_assembles_84(self):
        self.assertEqual([0x84, 0x44],
                         self.assemble('STY $44'))

    def test_assembles_85(self):
        self.assertEqual([0x85, 0x44],
                         self.assemble('STA $44'))

    def test_assembles_86(self):
        self.assertEqual([0x86, 0x44],
                         self.assemble('STX $44'))

    def dont_test_assembles_87(self):
        pass

    def test_assembles_87_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x87, 0x42],
                         self.assemble('SMB0 $42', 0x0000, mpu))

    def test_assembles_88(self):
        self.assertEqual([0x88],
                         self.assemble('DEY'))

    def dont_test_assembles_89(self):
        pass

    def test_assembles_89_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x89, 0x42],
                         self.assemble('BIT #$42', 0x0000, mpu))

    def test_assembles_8a(self):
        self.assertEqual([0x8a],
                         self.assemble('TXA'))

    def dont_test_assembles_8b(self):
        pass

    def test_assembles_8c(self):
        self.assertEqual([0x8c, 0x00, 0x44],
                         self.assemble('STY $4400'))

    def test_assembles_8d(self):
        self.assertEqual([0x8d, 0x00, 0x44],
                         self.assemble('STA $4400'))

    def test_assembles_8e(self):
        self.assertEqual([0x8e, 0x00, 0x44],
                         self.assemble('STX $4400'))

    def dont_test_assembles_8f(self):
        pass

    def test_assembles_90(self):
        self.assertEqual([0x90, 0x44],
                         self.assemble('BCC $0046'))

    def test_assembles_91(self):
        self.assertEqual([0x91, 0x44],
                         self.assemble('STA ($44),Y'))

    def dont_test_assembles_92(self):
        pass

    def test_assembles_92_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x92, 0x44],
                         self.assemble('STA ($44)', 0x0000, mpu))

    def dont_test_assembles_93(self):
        pass

    def test_assembles_94(self):
        self.assertEqual([0x94, 0x44],
                         self.assemble('STY $44,X'))

    def test_assembles_95(self):
        self.assertEqual([0x95, 0x44],
                         self.assemble('STA $44,X'))

    def test_assembles_96(self):
        self.assertEqual([0x96, 0x44],
                         self.assemble('STX $44,Y'))

    def dont_test_assembles_97(self):
        pass

    def test_assembles_97_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x97, 0x42],
                         self.assemble('SMB1 $42', 0x0000, mpu))

    def test_assembles_98(self):
        self.assertEqual([0x98],
                         self.assemble('TYA'))

    def test_assembles_99(self):
        self.assertEqual([0x99, 0x00, 0x44],
                         self.assemble('STA $4400,Y'))

    def test_assembles_9a(self):
        self.assertEqual([0x9a],
                         self.assemble('TXS'))

    def dont_test_assembles_9b(self):
        pass

    def dont_test_assembles_9c(self):
        pass

    def test_assembles_9c_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x9c, 0x34, 0x12],
                         self.assemble('STZ $1234', 0x0000, mpu))

    def test_assembles_9d(self):
        self.assertEqual([0x9d, 0x00, 0x44],
                         self.assemble('STA $4400,X'))

    def dont_test_assembles_9e(self):
        pass

    def test_assembles_9e_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0x9e, 0x34, 0x12],
                         self.assemble('STZ $1234,X', 0x0000, mpu))

    def dont_test_assembles_9f(self):
        pass

    def test_assembles_a0(self):
        self.assertEqual([0xa0, 0x44],
                         self.assemble('LDY #$44'))

    def test_assembles_a1(self):
        self.assertEqual([0xa1, 0x44],
                         self.assemble('LDA ($44,X)'))

    def test_assembles_a2(self):
        self.assertEqual([0xa2, 0x44],
                         self.assemble('LDX #$44'))

    def dont_test_assembles_a3(self):
        pass

    def test_assembles_a4(self):
        self.assertEqual([0xa4, 0x44],
                         self.assemble('LDY $44'))

    def test_assembles_a5(self):
        self.assertEqual([0xa5, 0x44],
                         self.assemble('LDA $44'))

    def test_assembles_a6(self):
        self.assertEqual([0xa6, 0x44],
                         self.assemble('LDX $44'))

    def dont_test_assembles_a7(self):
        pass

    def test_assembles_a7_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xa7, 0x42],
                         self.assemble('SMB2 $42', 0x0000, mpu))

    def test_assembles_a8(self):
        self.assertEqual([0xa8],
                         self.assemble('TAY'))

    def test_assembles_a9(self):
        self.assertEqual([0xa9, 0x44],
                         self.assemble('LDA #$44'))

    def test_assembles_aa(self):
        self.assertEqual([0xaa],
                         self.assemble('TAX'))

    def dont_test_assembles_ab(self):
        pass

    def test_assembles_ac(self):
        self.assertEqual([0xac, 0x00, 0x44],
                         self.assemble('LDY $4400'))

    def test_assembles_ad(self):
        self.assertEqual([0xad, 0x00, 0x44],
                         self.assemble('LDA $4400'))

    def test_assembles_ae(self):
        self.assertEqual([0xae, 0x00, 0x44],
                         self.assemble('LDX $4400'))

    def dont_test_assembles_af(self):
        pass

    def test_assembles_b0(self):
        self.assertEqual([0xb0, 0x44],
                         self.assemble('BCS $0046'))

    def test_assembles_b1(self):
        self.assertEqual([0xb1, 0x44],
                         self.assemble('LDA ($44),Y'))

    def dont_test_assembles_b2(self):
        pass

    def test_assembles_b2_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xb2, 0x44],
                         self.assemble('LDA ($44)', 0x0000, mpu))

    def dont_test_assembles_b3(self):
        pass

    def test_assembles_b4(self):
        self.assertEqual([0xb4, 0x44],
                         self.assemble('LDY $44,X'))

    def test_assembles_b5(self):
        self.assertEqual([0xb5, 0x44],
                         self.assemble('LDA $44,X'))

    def test_assembles_b6(self):
        self.assertEqual([0xb6, 0x44],
                         self.assemble('LDX $44,Y'))

    def dont_test_assembles_b7(self):
        pass

    def test_assembles_b7_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xb7, 0x42],
                         self.assemble('SMB3 $42', 0x0000, mpu))

    def test_assembles_b8(self):
        self.assertEqual([0xb8],
                         self.assemble('CLV'))

    def test_assembles_b9(self):
        self.assertEqual([0xb9, 0x00, 0x44],
                         self.assemble('LDA $4400,Y'))

    def test_assembles_ba(self):
        self.assertEqual([0xba],
                         self.assemble('TSX'))

    def dont_test_assembles_bb(self):
        pass

    def test_assembles_bc(self):
        self.assertEqual([0xbc, 0x00, 0x44],
                         self.assemble('LDY $4400,X'))

    def test_assembles_bd(self):
        self.assertEqual([0xbd, 0x00, 0x44],
                         self.assemble('LDA $4400,X'))

    def test_assembles_be(self):
        self.assertEqual([0xbe, 0x00, 0x44],
                         self.assemble('LDX $4400,Y'))

    def dont_test_assembles_bf(self):
        pass

    def test_assembles_c0(self):
        self.assertEqual([0xc0, 0x44],
                         self.assemble('CPY #$44'))

    def test_assembles_c1(self):
        self.assertEqual([0xc1, 0x44],
                         self.assemble('CMP ($44,X)'))

    def dont_test_assembles_c2(self):
        pass

    def dont_test_assembles_c3(self):
        pass

    def test_assembles_c4(self):
        self.assertEqual([0xc4, 0x44],
                         self.assemble('CPY $44'))

    def test_assembles_c5(self):
        self.assertEqual([0xc5, 0x44],
                         self.assemble('CMP $44'))

    def test_assembles_c6(self):
        self.assertEqual([0xc6, 0x44],
                         self.assemble('DEC $44'))

    def dont_test_assembles_c7(self):
        pass

    def test_assembles_c7_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xc7, 0x42],
                         self.assemble('SMB4 $42', 0x0000, mpu))

    def test_assembles_c8(self):
        self.assertEqual([0xc8],
                         self.assemble('INY'))

    def test_assembles_c9(self):
        self.assertEqual([0xc9, 0x44],
                         self.assemble('CMP #$44'))

    def test_assembles_ca(self):
        self.assertEqual([0xca],
                         self.assemble('DEX'))

    def dont_test_assembles_cb(self):
        pass

    def test_assembles_cb_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xcb],
                         self.assemble('WAI', 0x0000, mpu))

    def test_assembles_cc(self):
        self.assertEqual([0xcc, 0x00, 0x44],
                         self.assemble('CPY $4400'))

    def test_assembles_cd(self):
        self.assertEqual([0xcd, 0x00, 0x44],
                         self.assemble('CMP $4400'))

    def test_assembles_ce(self):
        self.assertEqual([0xce, 0x00, 0x44],
                         self.assemble('DEC $4400'))

    def dont_test_assembles_cf(self):
        pass

    def test_assembles_d0(self):
        self.assertEqual([0xd0, 0x44],
                         self.assemble('BNE $0046'))

    def test_assembles_d1(self):
        self.assertEqual([0xd1, 0x44],
                         self.assemble('CMP ($44),Y'))

    def dont_test_assembles_d2(self):
        pass

    def test_assembles_d2_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xd2, 0x42],
                         self.assemble('CMP ($42)', 0x0000, mpu))

    def dont_test_assembles_d3(self):
        pass

    def dont_test_assembles_d4(self):
        pass

    def test_assembles_d5(self):
        self.assertEqual([0xd5, 0x44],
                         self.assemble('CMP $44,X'))

    def test_assembles_d6(self):
        self.assertEqual([0xd6, 0x44],
                         self.assemble('DEC $44,X'))

    def dont_test_assembles_d7(self):
        pass

    def test_assembles_d7_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xd7, 0x42],
                         self.assemble('SMB5 $42', 0x0000, mpu))

    def test_assembles_d8(self):
        self.assertEqual([0xd8],
                         self.assemble('CLD'))

    def dont_test_assembles_da(self):
        pass

    def test_assembles_da_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xda],
                         self.assemble('PHX', 0x0000, mpu))

    def dont_test_assembles_db(self):
        pass

    def dont_test_assembles_dc(self):
        pass

    def test_assembles_dd(self):
        self.assertEqual([0xdd, 0x00, 0x44],
                         self.assemble('CMP $4400,X'))

    def test_assembles_de(self):
        self.assertEqual([0xde, 0x00, 0x44],
                         self.assemble('DEC $4400,X'))

    def dont_test_assembles_df(self):
        pass

    def test_assembles_e0(self):
        self.assertEqual([0xe0, 0x44],
                         self.assemble('CPX #$44'))

    def test_assembles_e1(self):
        self.assertEqual([0xe1, 0x44],
                         self.assemble('SBC ($44,X)'))

    def dont_test_assembles_e2(self):
        pass

    def dont_test_assembles_e3(self):
        pass

    def test_assembles_e4(self):
        self.assertEqual([0xe4, 0x44],
                         self.assemble('CPX $44'))

    def test_assembles_e5(self):
        self.assertEqual([0xe5, 0x44],
                         self.assemble('SBC $44'))

    def test_assembles_e6(self):
        self.assertEqual([0xe6, 0x44],
                         self.assemble('INC $44'))

    def dont_test_assembles_e7(self):
        pass

    def test_assembles_e7_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xe7, 0x42],
                         self.assemble('SMB6 $42', 0x0000, mpu))

    def test_assembles_e8(self):
        self.assertEqual([0xe8],
                         self.assemble('INX'))

    def test_assembles_e9(self):
        self.assertEqual([0xe9, 0x44],
                         self.assemble('SBC #$44'))

    def test_assembles_ea(self):
        self.assertEqual([0xea],
                         self.assemble('NOP'))

    def dont_test_assembles_eb(self):
        pass

    def test_assembles_ec(self):
        self.assertEqual([0xec, 0x00, 0x44],
                         self.assemble('CPX $4400'))

    def test_assembles_ed(self):
        self.assertEqual([0xed, 0x00, 0x44],
                         self.assemble('SBC $4400'))

    def test_assembles_ee(self):
        self.assertEqual([0xee, 0x00, 0x44],
                         self.assemble('INC $4400'))

    def dont_test_assembles_ef(self):
        pass

    def test_assembles_f0_forward(self):
        self.assertEqual([0xf0, 0x44],
                         self.assemble('BEQ $0046'))

    def test_assembles_f0_backward(self):
        self.assertEqual([0xf0, 0xfc],
                         self.assemble('BEQ $BFFE', pc=0xc000))

    def test_assembles_f1(self):
        self.assertEqual([0xf1, 0x44],
                         self.assemble('SBC ($44),Y'))

    def dont_test_assembles_f2(self):
        pass

    def test_assembles_f2_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xf2, 0x42],
                         self.assemble('SBC ($42)', 0x0000, mpu))

    def dont_test_assembles_f3(self):
        pass

    def dont_test_assembles_f4(self):
        pass

    def test_assembles_f5(self):
        self.assertEqual([0xf5, 0x44],
                         self.assemble('SBC $44,X'))

    def test_assembles_f6(self):
        self.assertEqual([0xf6, 0x44],
                         self.assemble('INC $44,X'))

    def dont_test_assembles_f7(self):
        pass

    def test_assembles_f7_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xf7, 0x42],
                         self.assemble('SMB7 $42', 0x0000, mpu))

    def test_assembles_f8(self):
        self.assertEqual([0xf8],
                         self.assemble('SED'))

    def test_assembles_f9(self):
        self.assertEqual([0xf9, 0x00, 0x44],
                         self.assemble('SBC $4400,Y'))

    def dont_test_assembles_fa(self):
        pass

    def test_assembles_fa_65c02(self):
        mpu = MPU65C02()
        self.assertEqual([0xfa],
                         self.assemble('PLX', 0x0000, mpu))

    def dont_test_assembles_fb(self):
        pass

    def dont_test_assembles_fc(self):
        pass

    def test_assembles_fd(self):
        self.assertEqual([0xfd, 0x00, 0x44],
                         self.assemble('SBC $4400,X'))

    def test_assembles_fe(self):
        self.assertEqual([0xfe, 0x00, 0x44],
                         self.assemble('INC $4400,X'))

    def dont_test_assembles_ff(self):
        pass

    # Test Helpers

    def assemble(self, statement, pc=0000, mpu=None):
        if mpu is None:
            mpu = MPU()
        address_parser = AddressParser()
        assembler = Assembler(mpu, address_parser)
        return assembler.assemble(statement, pc)


def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
