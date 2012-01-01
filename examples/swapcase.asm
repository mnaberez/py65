; trivial demo program: read input, swap case and write out

        ; assemble using Anton Treuenfels' HXA assembler
        ; with I6502.A macro file
        ;   HXA_TW.EXE swapcase.asm
        ; (runs on Linux if you have WINE installed)
        ; which will make
        ;   SWAPCASE.HEX
        ; where the first line should not be input to the hexloader

        .hexfile 

        .cpu T_32_M16 
        .assume BIT32=1032, BIT32R=3210 
        .include "i6502.a" 

; I/O is memory-mapped in py65: 
PUTC     = $f001 
GETC     = $f005 ; blocking input 

; the py65 hexload boot ROM will only load to $0200
 .ORG $200 

another 
        lda GETC 
        eor #$20   ; swap upper and lower case as a demo 
        sta PUTC 
        jmp another 
