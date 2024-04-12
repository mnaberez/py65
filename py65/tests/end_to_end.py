import os
import signal
import sys
import tempfile
import unittest

from py65.compat import unicode

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
        mon.expect_exact(unicode("Py65 Monitor"))
        self.addCleanup(mon.kill, signal.SIGINT)
        return mon

    def test_putc(self):
        mon = self._spawn()

        mon.sendline(unicode("add_label f001 putc"))

        mon.sendline(unicode("a c000 lda #'H"))
        mon.sendline(unicode("a c002 sta putc"))
        mon.sendline(unicode("a c005 lda #'I"))
        mon.sendline(unicode("a c007 sta putc"))
        mon.sendline(unicode("a c00a brk"))

        mon.sendline(unicode("g c000"))
        mon.expect_exact(unicode("HI"))
        mon.sendline(unicode("q"))

    def test_getc(self):
        mon = self._spawn()

        mon.sendline(unicode("add_label f004 getc"))

        mon.sendline(unicode("a c000 ldx #0"))
        mon.sendline(unicode("a c002 lda getc"))
        mon.sendline(unicode("a c005 beq c002"))
        mon.sendline(unicode("a c007 cmp #'!"))
        mon.sendline(unicode("a c009 bne c00c"))
        mon.sendline(unicode("a c00b brk"))
        mon.sendline(unicode("a c00c sta 1000,x"))
        mon.sendline(unicode("a c00f inx"))
        mon.sendline(unicode("a c010 jmp c002"))

        mon.sendline(unicode("g c000"))
        mon.send(unicode("HELLO!"))
        mon.expect_exact(unicode("6502:"))
        mon.sendline(unicode("m 1000:1004"))
        mon.expect_exact(unicode("48  45  4c  4c  4f"))

    def test_assemble_interactive(self):
        mon = self._spawn()

        mon.sendline(unicode("assemble 0"))
        mon.expect_exact(unicode("$0000"))

        mon.sendline(unicode("lda $1234"))
        mon.expect_exact(unicode("ad 34 12"))

        mon.expect_exact(unicode("$0003"))
        mon.sendline(unicode("sta $4567"))
        mon.expect_exact(unicode("8d 67 45"))

        mon.sendline(unicode("invalid"))
        mon.expect_exact(unicode("?Syntax"))

        mon.sendline()
        mon.sendline(unicode("quit"))

if __name__ == '__main__':
    unittest.main()
