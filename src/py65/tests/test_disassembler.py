import unittest
import sys
from py65.mpu6502 import MPU
from py65.disassembler import Disassembler
from py65.util import AddressParser

class DisassemblerTests(unittest.TestCase):
    def test_disassembles_00(self):
        length, disasm = self.disassemble([0x00])
        self.assertEqual(1, length)
        self.assertEqual('BRK', disasm)

    def test_disassembles_01(self):
        length, disasm = self.disassemble([0x01, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ORA ($44,X)', disasm)

    def test_disassembles_02(self):
        length, disasm = self.disassemble([0x02])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)
        
    def test_disassembles_03(self):
        length, disasm = self.disassemble([0x03])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)

    def test_disassembles_04(self):
        length, disasm = self.disassemble([0x04])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)

    def test_disassembles_05(self):
        length, disasm = self.disassemble([0x05, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ORA $44', disasm)

    def test_disassembles_06(self):
        length, disasm = self.disassemble([0x06, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ASL $44', disasm)

    def test_disassembles_07(self):
        length, disasm = self.disassemble([0x07])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)

    def test_disassembles_08(self):
        length, disasm = self.disassemble([0x08])
        self.assertEqual(1, length)
        self.assertEqual('PHP', disasm)        

    def test_disassembles_09(self):
        length, disasm = self.disassemble([0x09, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ORA #$44', disasm)       

    def test_disassembles_10(self):
        length, disasm = self.disassemble([0x10, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('BPL $0046', disasm)       

    def test_disassembles_11(self):
        length, disasm = self.disassemble([0x11, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ORA ($44),Y', disasm)       

    def test_disassembles_12(self):
        length, disasm = self.disassemble([0x12])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)         

    def test_disassembles_13(self):
        length, disasm = self.disassemble([0x13])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)         

    def test_disassembles_14(self):
        length, disasm = self.disassemble([0x14])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)         

    def test_disassembles_15(self):
        length, disasm = self.disassemble([0x15, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ORA $44,X', disasm)         

    def test_disassembles_16(self):
        length, disasm = self.disassemble([0x16, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ASL $44,X', disasm)   
        
    def test_disassembles_17(self):
        length, disasm = self.disassemble([0x17])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)   
        
    def test_disassembles_18(self):
        length, disasm = self.disassemble([0x18])
        self.assertEqual(1, length)
        self.assertEqual('CLC', disasm)   
        
    def test_disassembles_19(self):
        length, disasm = self.disassemble([0x19, 0x00, 0x44])
        self.assertEqual(3, length)
        self.assertEqual('ORA $4400,Y', disasm)           
        
    def test_disassembles_20(self):
        length, disasm = self.disassemble([0x20, 0x97, 0x55])
        self.assertEqual(3, length)
        self.assertEqual('JSR $5597', disasm)           

    def test_disassembles_21(self):
        length, disasm = self.disassemble([0x21, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('AND ($44,X)', disasm)           

    def test_disassembles_22(self):
        length, disasm = self.disassemble([0x22])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)           

    def test_disassembles_23(self):
        length, disasm = self.disassemble([0x23])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)       

    def test_disassembles_24(self):
        length, disasm = self.disassemble([0x24, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('BIT $44', disasm)                              

    def test_disassembles_25(self):
        length, disasm = self.disassemble([0x25, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('AND $44', disasm)                              

    def test_disassembles_26(self):
        length, disasm = self.disassemble([0x26, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ROL $44', disasm)          

    def test_disassembles_27(self):
        length, disasm = self.disassemble([0x27])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)          

    def test_disassembles_28(self):
        length, disasm = self.disassemble([0x28])
        self.assertEqual(1, length)
        self.assertEqual('PLP', disasm)          

    def test_disassembles_29(self):
        length, disasm = self.disassemble([0x29, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('AND #$44', disasm)          

    def test_disassembles_30(self):
        length, disasm = self.disassemble([0x30, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('BMI $0046', disasm)                          

    def test_disassembles_31(self):
        length, disasm = self.disassemble([0x31, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('AND ($44),Y', disasm)                          

    def test_disassembles_32(self):
        length, disasm = self.disassemble([0x32])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)          
 
    def test_disassembles_33(self):
        length, disasm = self.disassemble([0x33])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)                   
 
    def test_disassembles_34(self):
        length, disasm = self.disassemble([0x34])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)                   

    def test_disassembles_35(self):
        length, disasm = self.disassemble([0x35, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('AND $44,X', disasm)                   

    def test_disassembles_36(self):
        length, disasm = self.disassemble([0x36, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ROL $44,X', disasm)                                          
 
    def test_disassembles_37(self):
        length, disasm = self.disassemble([0x37])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)                   
 
    def test_disassembles_38(self):
        length, disasm = self.disassemble([0x38])
        self.assertEqual(1, length)
        self.assertEqual('SEC', disasm)    

    def test_disassembles_39(self):
        length, disasm = self.disassemble([0x39, 0x00, 0x44])
        self.assertEqual(3, length)
        self.assertEqual('AND $4400,Y', disasm)    
                                
    def test_disassembles_40(self):
        length, disasm = self.disassemble([0x40])
        self.assertEqual(1, length)
        self.assertEqual('RTI', disasm)    

    def test_disassembles_41(self):
        length, disasm = self.disassemble([0x41, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('EOR ($44,X)', disasm)    
 
    def test_disassembles_42(self):
        length, disasm = self.disassemble([0x42])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)                   

    def test_disassembles_43(self):
        length, disasm = self.disassemble([0x43])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)                                      

    def test_disassembles_44(self):
        length, disasm = self.disassemble([0x44])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)                                      

    def test_disassembles_45(self):
        length, disasm = self.disassemble([0x45, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('EOR $44', disasm)          

    def test_disassembles_46(self):
        length, disasm = self.disassemble([0x46, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('LSR $44', disasm)          

    def test_disassembles_47(self):
        length, disasm = self.disassemble([0x47])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)      

    def test_disassembles_48(self):
        length, disasm = self.disassemble([0x48])
        self.assertEqual(1, length)
        self.assertEqual('PHA', disasm)      

    def test_disassembles_49(self):
        length, disasm = self.disassemble([0x49, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('EOR #$44', disasm)      

    def test_disassembles_50(self):
        length, disasm = self.disassemble([0x50, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('BVC $0046', disasm)      

    def test_disassembles_51(self):
        length, disasm = self.disassemble([0x51, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('EOR ($44),Y', disasm)      

    def test_disassembles_52(self):
        length, disasm = self.disassemble([0x52])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)      

    def test_disassembles_53(self):
        length, disasm = self.disassemble([0x53])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)      

    def test_disassembles_54(self):
        length, disasm = self.disassemble([0x54])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)                  

    def test_disassembles_55(self):
        length, disasm = self.disassemble([0x55, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('EOR $44,X', disasm)              

    def test_disassembles_56(self):
        length, disasm = self.disassemble([0x56, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('LSR $44,X', disasm)              

    def test_disassembles_57(self):
        length, disasm = self.disassemble([0x57])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)              

    def test_disassembles_58(self):
        length, disasm = self.disassemble([0x58])
        self.assertEqual(1, length)
        self.assertEqual('CLI', disasm)              

    def test_disassembles_59(self):
        length, disasm = self.disassemble([0x59, 0x00, 0x44])
        self.assertEqual(3, length)
        self.assertEqual('EOR $4400,Y', disasm)                      

    def test_disassembles_60(self):
        length, disasm = self.disassemble([0x60])
        self.assertEqual(1, length)
        self.assertEqual('RTS', disasm)                      

    def test_disassembles_61(self):
        length, disasm = self.disassemble([0x61, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ADC ($44,X)', disasm)        

    def test_disassembles_62(self):
        length, disasm = self.disassemble([0x61, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ADC ($44,X)', disasm)      

    def test_disassembles_63(self):
        length, disasm = self.disassemble([0x63])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)              

    def test_disassembles_64(self):
        length, disasm = self.disassemble([0x64])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)              

    def test_disassembles_65(self):
        length, disasm = self.disassemble([0x65, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ADC $44', disasm)           

    def test_disassembles_66(self):
        length, disasm = self.disassemble([0x66, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ROR $44', disasm)    

    def test_disassembles_67(self):
        length, disasm = self.disassemble([0x67])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)            

    def test_disassembles_68(self):
        length, disasm = self.disassemble([0x68])
        self.assertEqual(1, length)
        self.assertEqual('PLA', disasm)   

    def test_disassembles_69(self):
        length, disasm = self.disassemble([0x69, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ADC #$44', disasm)

    def test_disassembles_70(self):
        length, disasm = self.disassemble([0x70, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('BVS $0046', disasm)

    def test_disassembles_71(self):
        length, disasm = self.disassemble([0x71, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ADC ($44),Y', disasm)   

    def test_disassembles_72(self):
        length, disasm = self.disassemble([0x72])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)            

    def test_disassembles_73(self):
        length, disasm = self.disassemble([0x73])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)                                                               

    def test_disassembles_74(self):
        length, disasm = self.disassemble([0x74])
        self.assertEqual(1, length)
        self.assertEqual('???', disasm)    

    def test_disassembles_75(self):
        length, disasm = self.disassemble([0x75, 0x44])
        self.assertEqual(2, length)
        self.assertEqual('ADC $44,X', disasm)    
        
    # Test Helpers
    
    def disassemble(self, bytes):
        mpu = MPU()
        address_parser = AddressParser()
        disasm = Disassembler(mpu, address_parser)
        mpu.memory[0:len(bytes)-1] = bytes
        return disasm.instruction_at(0)
  
def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
