import os
import signal
import sys
import tempfile
import unittest


# end-to-test tests are slow so only run them when asked
if 'END_TO_END' in os.environ:
    if sys.platform == "win32":
        raise NotImplementedError()
    else:
        import pexpect
        BaseTestCase = unittest.TestCase
else:
    BaseTestCase = object


class EndToEndTests(BaseTestCase):

    def _spawn(self):
        mon = pexpect.spawn(
            sys.executable, 
            ['-u', '-m', 'py65.monitor'], 
            encoding='utf-8'
            )
        mon.expect_exact("Py65 Monitor")
        self.addCleanup(mon.kill, signal.SIGINT)
        return mon

    def test_putc(self):
        mon = self._spawn()

        mon.sendline("add_label f001 putc")

        mon.sendline("a c000 lda #'H")
        mon.sendline("a c002 sta putc")
        mon.sendline("a c005 lda #'I")
        mon.sendline("a c007 sta putc")
        mon.sendline("a c00a brk")

        mon.sendline("g c000")
        mon.expect_exact("HI")
        mon.sendline("q")

    def test_getc(self):
        mon = self._spawn()

        mon.sendline("add_label f004 getc")

        mon.sendline("a c000 ldx #0")
        mon.sendline("a c002 lda getc")
        mon.sendline("a c005 beq c002")
        mon.sendline("a c007 cmp #'!")
        mon.sendline("a c009 bne c00c")
        mon.sendline("a c00b brk")
        mon.sendline("a c00c sta 1000,x")
        mon.sendline("a c00f inx")
        mon.sendline("a c010 jmp c002")

        mon.sendline("g c000")
        mon.send("HELLO!")
        mon.expect_exact("6502:")
        mon.sendline("m 1000:1004")
        mon.expect_exact("48  45  4c  4c  4f")

    def test_assemble_interactive(self):
        mon = self._spawn()

        mon.sendline("assemble 0")
        mon.expect_exact("$0000")

        mon.sendline("lda $1234")
        mon.expect_exact("ad 34 12")

        mon.expect_exact("$0003")
        mon.sendline("sta $4567")
        mon.expect_exact("8d 67 45")

        mon.sendline("invalid")
        mon.expect_exact("?Syntax")

        mon.sendline()
        mon.sendline("quit")

if __name__ == '__main__':
    unittest.main()
