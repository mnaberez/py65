 .LIST

; bootrom for py65 monitor in 65Org16 mode
; based on
; Intel Hex format loader by Ross Archer (9 February 2001, freeware)
; from http: http://www.6502.org/source/monitors/intelhex/intelhex.htm
;

; use this monitor like this:
;   PYTHONPATH=. python py65/monitor.py -m 65Org16
;   load bootrom.bin fe00
;   goto fe00

START = $FFFFFe00

; I/O is memory-mapped in py65:
PUTC     = $f001
GETC     = $f005 ; blocking input

; Note that Hex format for 65Org16 uses ';' not ':' as the start of record mark
; also note that some fields are now composed of 16-bit elements:
; previously:
;  length offset type   data     checksum
;     :/08/E008/00/08090A0B0C0D0E0F/xx 
; now
;     ;/10/E008/00/00080009000A000B000C000D000E000F/xx 

; Zero-page storage
DPL       =  $00 ; data pointer (two bytes) used by PUTSTRI
DPH       =  $01 ; high of data pointer
RECLEN    =  $02 ; record length in bytes
START_LO  =  $03
START_HI  =  $04
RECTYPE   =  $05
CHKSUM    =  $06 ; record checksum accumulator
DLFAIL    =  $07 ; flag for download failure
TEMP      =  $08 ; save hex value
TMPHEX    =  $09 ; save another hex value

	; where the RAM program MUST have its first instruction
ENTRY_POINT  =  $0200

 .ORG START

        sei                     ; disable interrupts
        cld                     ; binary mode arithmetic
        ldx     #$1FFFF         ; Set up the stack pointer
        txs                     ;       "

        ; Download Intel hex.  The program you download MUST have its entry
        ; instruction (even if only a jump to somewhere else) at ENTRY_POINT.
HEXDNLD lda     #0
        sta     START_HI        ; store all programs in bank 0 (page 0) for now
        sta     DLFAIL          ;Start by assuming no D/L failure
        jsr     PUTSTRI
        .byte   13,10,13,10
        .byte   "Send 65Org16 code in"
        .byte   " variant Intel Hex format"
        .byte  " at 19200,n,8,1 ->"
        .byte   13,10
	.byte	0		; Null-terminate unless you prefer to crash.
HDWRECS jsr     GETSER          ; Wait for start of record mark ';'
        cmp     #';'
        bne     HDWRECS         ; not found yet
        ; Start of record marker has been found
        lda     #0
        sta     CHKSUM
        jsr     GETHEX          ; Get the record length
        sta     RECLEN          ; save it
        jsr     GET4HX          ; Get the 16-bit offset
        sta     START_LO
        jsr     GETHEX          ; Get the record type
        sta     RECTYPE         ; & save it
        bne     HDER1           ; end-of-record
        ldx     RECLEN          ; number of data bytes to write to memory
        ldy     #0              ; start offset at 0
HDLP1   jsr     GET4HX          ; Get the first/next/last data word
        sta     (START_LO),y    ; Save it to RAM
        iny                     ; update data pointer
        dex                     ; decrement character count
        dex                     ; ... twice
        bne     HDLP1
        jsr     GETHEX          ; get the checksum
        lda     CHKSUM
        bne     HDDLF1          ; If failed, report it
        ; Another successful record has been processed
        lda     #'#'            ; Character indicating record OK = '#'
        sta     PUTC            ; write it out but don't wait for output 
        jmp     HDWRECS         ; get next record     
HDDLF1  lda     #'F'            ; Character indicating record failure = 'F'
        sta     DLFAIL          ; download failed if non-zero
        sta     PUTC            ; write it to transmit buffer register
        jmp     HDWRECS         ; wait for next record start
HDER1   cmp     #1              ; Check for end-of-record type
        beq     HDER2
        jsr     PUTSTRI         ; Warn user of unknown record type
        .byte   13,10,13,10
        .byte   "Unknown record type $"
	.byte	0		; null-terminate unless you prefer to crash!
        lda     RECTYPE         ; Get it
	sta	DLFAIL		; non-zero --> download has failed
        jsr     PUTHEX          ; print it
	lda     #13		; but we'll let it finish so as not to 
        jsr     PUTSER		; falsely start a new d/l from existing 
        lda     #10		; file that may still be coming in for 
        jsr     PUTSER		; quite some time yet.
	jmp	HDWRECS
	; We've reached the end-of-record record
HDER2   jsr     GETHEX          ; get the checksum 
        lda     CHKSUM          ; Add previous checksum accumulator value
        beq     HDER3           ; checksum = 0 means we're OK!
        jsr     PUTSTRI         ; Warn user of bad checksum
        .byte   13,10,13,10
        .byte   "Bad record checksum!",13,10
        .byte   0		; Null-terminate or 6502 go bye-bye
        jmp     START
HDER3   lda     DLFAIL
        beq     HDEROK
        ;A download failure has occurred
        jsr     PUTSTRI
        .byte   13,10,13,10
        .byte   "Download Failed",13,10
        .byte   "Aborting!",13,10
	.byte	0		; null-terminate every string yada yada.
        jmp     START
HDEROK  jsr     PUTSTRI
        .byte   13,10,13,10
        .byte   "Download Successful!",13,10
        .byte   "Jumping to location $"
	.byte	0			; by now, I figure you know what this is for. :)
        lda	#HI(ENTRY_POINT)	; Print the entry point in hex
        jsr	PUTHEX
        lda	#LO(ENTRY_POINT)
	jsr	PUTHEX
        jsr	PUTSTRI
        .byte   13,10
        .byte   0		; stop lemming-like march of the program ctr. thru data
        jmp     ENTRY_POINT	; jump to canonical entry point

; For py65, the input routine will block until a character arrives
GETSER  lda     GETC
        rts

; get four ascii chars, adding both octets into the checksum
GET4HX  jsr     GETHEX
        asl a
        asl a
        asl a
        asl a
        asl a
        asl a
        asl a
        asl a
        sta     TMPHEX
        jsr     GETHEX
        ora     TMPHEX
        rts

; get two ascii chars, add into the checksum
GETHEX  jsr     GETSER
        jsr     MKNIBL  	; Convert to 0..F numeric
        asl     a
        asl     a
        asl     a
        asl     a       	; This is the upper nibble
        and     #$F0
        sta     TEMP
        jsr     GETSER
        jsr     MKNIBL
        ora     TEMP
        sta     TEMP
        clc
        adc     CHKSUM          ; Add in the checksum
        and     #$ff
        sta     CHKSUM          ;
        lda     TEMP
        rts             	; return with the nibble received

; Convert the ASCII nibble to numeric value from 0-F:
MKNIBL  cmp     #'9'+1  	; See if it's 0-9 or 'A'..'F' (no lowercase yet)
        bcc     MKNNH   	; If we borrowed, we lost the carry so 0..9
        sbc     #7+1    	; Subtract off extra 7 (sbc subtracts off one less)
        ; If we fall through, carry is set unlike direct entry at MKNNH
MKNNH   sbc     #'0'-1  	; subtract off '0' (if carry clear coming in)
        and     #$0F    	; no upper nibble no matter what
        rts             	; and return the nibble

; Put byte in A as hexydecascii
PUTHEX  pha             	;
        lsr a
        lsr a
        lsr a
        lsr a
        jsr     PRNIBL
        pla
PRNIBL  and     #$0F    	; strip off the low nibble
        cmp     #$0A    
        bcc     NOTHEX  	; if it's 0-9, add '0' else also add 7
        adc     #6      	; Add 7 (6+carry=1), result will be carry clear
NOTHEX  adc     #'0'    	; If carry clear, we're 0-9
; Write the character in A as ASCII:
PUTSER  sta     PUTC
        rts

;Put the string following in-line until a NULL out to the console
PUTSTRI pla			; Get the low part of "return" address (data start address)
        sta     DPL     
        pla 
        sta     DPH             ; Get the high part of "return" address
                                ; (data start address)
        ; Note: actually we're pointing one short
PSINB   ldy     #1
        lda     (DPL),y         ; Get the next string character
        inc     DPL             ; update the pointer
        bne     PSICHO          ; if not, we're pointing to next character
        inc     DPH             ; account for page crossing
PSICHO  ora     #0              ; Set flags according to contents of Accumulator
        beq     PSIX1           ; don't print the final NULL 
        jsr     PUTSER          ; write it out
        jmp     PSINB           ; back around
PSIX1   inc     DPL             ; 
        bne     PSIX2           ;
        inc     DPH             ; account for page crossing
PSIX2   jmp     (DPL)           ; return to byte following final NULL
;
; Dummy interrupt handlers
GOIRQ
GONMI   RTI

; vectors               
 .ORG $FFFFFFFA
NMIENT  .word     GONMI
RSTENT  .word     START
IRQENT  .word     GOIRQ
.end				; finally.  das Ende.
