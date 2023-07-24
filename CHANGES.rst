2.0.0.dev0 (Next Release)
-------------------------

- Support for some older Python versions has been dropped.  Py65
  now requires Python 3.6 or later.

- Fixed a bug with character input that would cause characters to be
  dropped when pasting in larger amounts of text.  This makes it possible
  to paste programs into EhBASIC and Taliforth.  Patch by SamCoVT.

- The ``fill`` command in the monitor now shows an error message if an
  address or value is out of range.

- Added ``irq()`` and ``nmi()`` methods to the ``MPU`` class, so that
  interrupts can be simulated. Patch by Irmen de Jong.

- The ``MPU`` class constructor now accepts ``None`` for the initial PC, which
  will cause it to read the address from the reset vector on ``reset()``.

- The ``py65`` package is no longer a namespace package.

1.1.0 (2018-07-01)
------------------

- The ``Monitor`` class now allows the default memory to be supplied in
  the constructor.  Patch by Irmen de Jong.

- Fixed a bug where setting the MPU via ``py65mon`` command line arguments
  would have no effect.  Reported by Michael A. Morris, patch by Ed Spittles.

- The ``itoa()`` function in ``conversions.py`` now raises an error when an
  unsupported base is given.  Patch by Scot W. Stevenson.

- The unused hexdump loader utility has been removed.

1.0.0 (2017-05-11)
------------------

- Fixed a bug where the ordering of ``py65mon`` command line arguments
  produced different results.  Arguments can now be specified in any
  order.  Patch by Mario Keller.

- Added new ``--input`` and ``--output`` arguments to ``py65mon`` that
  allow the addresses of the ``getc`` and ``putc`` handlers to be
  changed.  Patch by Mario Keller.

- Fixed a 65C02 bug where the TSB and TRB instructions did not set
  the Z flag correctly.  Thanks to Kris Kennaway for reporting it.

0.24 (2015-03-31)
-----------------

- Released as a universal wheel.

0.23 (2015-02-10)
-----------------

- Added a workaround to $F001 output to catch encoding errors and
  display a "?" instead of crashing.  This condition can occur if
  the 6502 program sends bytes to $F001 that aren't compatible with
  the terminal's character encoding.

0.22 (2015-02-09)
-----------------

- Fixed a bug where ``py65mon --rom`` would raise an exception
  on Python 3.

0.21 (2015-02-09)
-----------------

- Added support for breakpoints in the monitor.  Contributed by
  Alessandro Gatti.

- ASCII literals are now supported by the assembler.  The statement
  "LDA #'A'" is equivalent to "LDA #$41".

- Fixed console input when run under Python 3 on Windows.  Closes #27.

0.20 (2014-05-08)
-----------------

- Page wrapping for indexed indirect (X) operations on 65C02 has been
  restored.  This reverts the change introduced in 0.18.  We now believe
  that this mode works the same on the 65C02 as it does on the 6502.

0.19 (2014-03-12)
-----------------

- Fixed 65C02 opcode $D2: CMP Zero Page, Indirect.

- Blocking character input at $F005 has been removed.  The I/O area
  was designed to be compatible with Michal Kowalski's simulator,
  and it uses this address for another purpose.  Examples that depended
  on $F005 have been changed to use $F004.

0.18 (2014-01-30)
-----------------

- Fixed a bug in RTS where popping $FFFF off the stack would cause
  the program counter to overflow to $10000.  It now wraps around
  to $0000 as it should.  Thanks to Gábor Lénárt for reporting it.

- Fixed BRK on 65C02 so it clears the decimal flag.  On NMOS 6502, the
  decimal flag is unaffected on BRK.  On 65C02, it is always cleared.

- Assembling now tolerates extra whitespace between opcode and operand.

- Removed page wrap bug from JMP indirect on 65C02.

- Removed page wrap bug from indexed indirect (X) operations on 65C02.

0.17 (2013-10-26)
-----------------

- Added support for Python 3.2 and 3.3 based on work by David Beazley.

0.16 (2013-04-03)
-----------------

- Fixed a bug in the monitor that caused loading from the command
  line with "--rom" to crash.

0.15 (2013-01-06)
-----------------

- Disassembling can now wrap around memory if the start address
  given is greater than the end address.

- Fixed the disassembler to accept a range of "start:end" instead of
  "start:end+1" for consistency with the other commands.

0.14 (2012-11-30)
-----------------

- Assembling now detects syntax errors, overflows, and bad labels
  separately and shows specific error messages.

- Fixed assembling 65C02 opcodes whose mnemonics have a digit
  such as "RMB3".

- Reformatted source code to comply with PEP8.

- Fixed a bug where the MPU status display would wrap unexpectedly
  on some terminals.

- Added support for 65C02 opcode 0x89: BIT #.

- Added support for 65C02 opcode 0x7C: JMP (abs,x).

- Assembling now shows an Overflow Error if the statement won't
  fit at the top of memory.

- Fixed a bug in the disassembler where instructions that wrap past
  the top of memory would not be displayed properly.

0.13 (2012-11-15)
-----------------

- Fixed a bug where negative numbers could be entered
  for addresses in the monitor.

0.12 (2012-02-16)
-----------------

- Fixed a bug that caused ``help cd`` to raise an exception
  in the monitor.

- Fixed a bug in the 65C02 simulation where the opcode 0x7A
  was named "PHY" instead of "PLY", causing incorrect assembly
  and disassembly.  Thanks to Brian Cassidy for reporting it.

- Fixed the cycle count of 0xD2 (CMP zero page indirect) in
  the 65C02 simulation.  Thanks to Brian Cassidy for reporting it.

- Added "h" as a monitor shortcut for "help".

0.11 (2012-01-07)
-----------------

- Added a new 65Org16 MPU simulation written by Ed Spittles.

- The monitor now accepts command line arguments.  See
  ``py65mon --help`` for usage.  Contributed by Ed Spittles.

- The monitor's load command can now fetch URLs.

- Python versions earlier than 2.6 are no longer supported.

0.10 (2011-08-27)
-----------------

- Fixed long-standing bugs in relative branch calculations in the
  assembler and disassembler.  Based on a patch by Ed Spittles.

- Zero page operations now have the correct page wrap around.
  Patch by Martti Kühne.

0.9 (2011-03-27)
----------------

- Fixed two monitor tests that were broken under Windows.  Thanks
  to Oscar Lindberg for reporting this.

- Removed use of defaultdict to fix compatibility with Python 2.4.

- Decimal mode bugs have been fixed.  Thanks to Ed Spittles who
  ported Bruce Clark's tests to find failures and then rewrote
  the decimal handling code.

0.8 (2010-03-08)
----------------

- Fixed deprecation warnings on Python 2.6

- We no longer bundle ez_setup to bootstrap setuptools installation.

- Restoring the processor status register from interrupt now correctly
  set the BREAK and UNUSED flags to be high.  Thanks to Ed Spittles
  for reporting this.

- Applied patch by Ed Spittles that fixes the behavior of the BREAK
  and UNUSED flags in the processor status register.  Closes #16.

- Added ">" as a monitor shortcut for the fill command for
  consistency with VICE.

0.7 (2009-09-03)
----------------

- When using the monitor, the nonblocking character input at
  $F004 should now work on the Microsoft Windows platform.

- Fixed that relative branch calculations would not use the correct
  start address when assembling in the monitor.  Closes #10.

- The processor status register ("p" or "flags") can now be changed
  in the monitor using the "registers" command with an argument of
  "p", such as "registers p=00".

- MPU objects now return a two-line string as their __repr__ with
  the processor status register displayed as binary for readability.

- The processor status register is now initialized to 0 on reset.
  Previously, its unused bit (bit 5) was set to 1 on reset.

- Applied patch from Ed Spittles to change the CMP algorithm so that
  it no longer fails Rob Finch's test suite.  Closes #8.

- Added a new interactive assembly mode to the monitor.  Entering the
  the assemble command with a statement such as "a c000 lda #0" works
  as before.  Entering "a c000" will start the interactive assembler
  at that address.  Entering "a" alone will start it at the current
  program counter.

- Applied patch from Ed Spittles so that SBC now properly sets the
  Overflow (V) flag.  This fixes a failure in Rob Finch's test suite.
  Closes #6.

- Applied patch from Ed Spittles so that SBC now properly sets the
  Carry (C) and Zero (Z) flags.  This fixes failures caught by Ed's
  own tests (see http://forum.6502.org/viewtopic.php?p=8854#8854).
  Closes #15.

- A new "save" command has been added to the monitor that will save
  a range of memory to a binary file.

0.6 (2009-08-11)
----------------

- Added monitor shortcut "a" for "assemble".

- Fixed that ASL would not properly set the Z flag.  Closes #7.

- Fixed that ADC would not properly set the Overflow (V) flag.  The
  overflow calculation that is now used originated from XGS: Apple
  IIGS Emulator (cputable.h).  Originally written and Copyright
  (C)1996 by Joshua M. Thompson.  Copyright (C) 2006 by Samuel A.
  Falvo II.  http://bitbucket.org/kc5tja/lib65816/src/tip/src/cputable.h
  Closes #3.

0.5 (2009-08-06)
----------------

- Fixed signatures of getc/putc callbacks in monitor that were broken
  when the ObservableMemory interface changed in 0.3.  Closes #1.

- Fixed that ROL would not properly set the Z flag.  Closes #2.

0.4 (2009-06-06)
----------------

- Added ez_setup.py to bootstrap setuptools installation.

0.3 (2009-06-03)
----------------

- Added shortcuts for monitor commands such as "m" for "memory".  These
  are mostly the same as the VICE monitor shortcuts.

- The terminal width can now be changed in the monitor using the new
  "width" command.  Some commands, like "mem", will wrap to this width.

- Fixed a bug where BRK would increment PC by 3 instead of 2.  Thanks
  to Oscar Lindberg.

- Added a new 65C02 MPU simulation started by Oscar Lindberg.  It is
  now mostly complete.

- Added a new "mpu" command to the monitor.  It will switch between the
  NMOS 6502 and CMOS 65C02 simulations.

- A new "devices" module has been added to organize device simulations.

- The mpu6502 and mpu65c02 devices have been reorganized internally to
  use Python decorators to build their lookup tables based on an
  idea by Oscar Lindberg.

- A new "utils" module has been added with various utility functions.

- The ObservableMemory interface has been changed for clarity.

- Python 2.4 or later is now required.

0.2 (2008-11-09)
----------------

- Added a new "disassemble" command to the monitor.  It can disassemble
  any range of memory ("disassemble c000:c010").  If labels have been
  defined, the disassembly will show them in the operands.

- Added a new "assemble" command to the monitor.  It can assemble a
  single instruction at an address ("assemble c000 jsr $ffd2").
  Labels in the operands are also supported ("assemble c000 jsr charout").

- Moved the character I/O area from $E000 to $F000 for compatibility with
  the EhBASIC binary saved from Michal Kowalski's Windows-based simulator.
  In a future version of Py65, the I/O area will be configurable.

- When running a program in the monitor, a read to $F004 will now do a
  non-blocking read from STDIN.  If no character is available, a null
  byte ($00) will be returned.

- Fixed a bug where a CMP instruction could crash the simulator due to
  an undefined variable.

- EhBASIC 2.09 now runs in the simulator!

- Documented all remaining monitor commands.  In the monitor, use the
  command "help command" for help on any command.

0.1 (2008-11-21)
----------------

- First release.
