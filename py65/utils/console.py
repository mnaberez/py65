import sys

from py65.compat import as_string

if sys.platform[:3] == "win":
    import msvcrt

    def get_unbuffered_stdin(stdin):
        """ get_unbuffered_stdin returns the given stdin on Windows. """
        return stdin

    def save_mode(stdin):
        """ save_mode is a no-op on Windows. """
        return

    def noncanonical_mode(stdin):
        """ noncanonical_mode is a no-op on Windows. """
        return

    def restore_mode():
        """ restore_mode is a no-op on Windows. """
        return

    def getch(stdin):
        """ Read one character from the Windows console, blocking until one
        is available.  Does not echo the character.  The stdin argument is
        for function signature compatibility and is ignored.
        """
        return as_string(msvcrt.getch())

    def getch_noblock(stdin):
        """ Read one character from the Windows console without blocking.
        Does not echo the character.  The stdin argument is for function
        signature compatibility and is ignored.  If no character is
        available, an empty string is returned.
        """
        if msvcrt.kbhit():
            return as_string(getch(stdin))
        return u''

else:
    import termios
    import os
    from select import select

    oldattr = None
    oldstdin = None

    def get_unbuffered_stdin(stdin):
        """ Attempt to get and return a copy of stdin that is
        unbuffered.  This allows for immediate response to typed input
        as well as pasted input.  If unable to get an unbuffered
        version of stdin, return the original version.
        """
        if stdin != None:
            try:
                # Reopen stdin with no buffer.
                return os.fdopen(os.dup(stdin.fileno()), 'rb', 0)
            except Exception as e:
                print(e)
                # Unable to reopen this file handle with no buffer.
                # Just use the original file handle.
                return stdin
        else:
            # If stdin is None, try using sys.stdin for input.
            try:
                # Reopen the system's stdin with no buffer.
                return os.fdopen(os.dup(sys.stdin.fileno()), 'rb', 0)
            except:
                # If unable to get an unbuffered stdin, just return
                # None, which is what we started with if we got here.
                return None

    def save_mode(stdin):
        """ For operating systems that support it, save the original
        input termios settings so they can be restored later.  This
        allows us to switch to noncanonical mode when software is
        running in the simulator and back to the original mode when
        accepting commands.
        """
        # For non-Windows systems, save the original input settings,
        # which will typically be blocking reads with echo.
        global oldattr
        global oldstdin

        # When the input is not a pty/tty, this will fail.
        # In that case, it's ok to ignore the failure.
        try:
            # Save the current terminal setup.
            oldstdin = stdin
            fd = stdin.fileno()
            oldattr = termios.tcgetattr(fd)
        except:
            # Quietly ignore termios errors, such as stdin not being
            # a tty.
            pass

    def noncanonical_mode(stdin):
        """For operating systems that support it, switch to noncanonical
        mode.  In this mode, characters are given immediately to the
        program and no processing of editing characters (like backspace)
        is performed.  Echo is also turned off in this mode.  The
        previous input behavior can be restored with restore_mode.
        """
        # For non-windows systems, switch to non-canonical
        # and no-echo non-blocking-read mode.
        try:
            # Save the current terminal setup.
            fd = stdin.fileno()
            currentattr = termios.tcgetattr(fd)
            # Switch to noncanonical (instant) mode with no echo.
            newattr = currentattr[:]
            newattr[3] &= ~termios.ICANON & ~termios.ECHO

            # Switch to non-blocking reads with no timeout.
            newattr[6][termios.VMIN] = 0
            newattr[6][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSANOW, newattr)
        except:
            # Quietly ignore termios errors, such as stdin not being
            # a tty.
            pass

    def restore_mode():
        """For operating systems that support it, restore the previous
        input mode.
        """

        # Restore the previous input setup.
        global oldattr
        global oldstdin

        try:
            # Restore the original system stdin.
            oldfd = oldstdin.fileno()
            # If there is a previous setting, restore it.
            if oldattr != None:
                # Restore it on the original system stdin.
                termios.tcsetattr(oldfd, termios.TCSANOW, oldattr)
        except:
            # Quietly ignore termios errors, such as stdin not being a tty.
            pass

    def getch(stdin):
        """ Read one character from stdin, blocking until one is available.
        Does not echo the character.
        """
        # Try to get a character with a non-blocking read.
        char = ''
        noncanonical_mode(stdin)
        # If we didn't get a character, ask again.
        while char == '':
            try:
                # On OSX, calling read when no data is available causes the
                # file handle to never return any future data, so we need to
                # use select to make sure there is at least one char to read.
                rd,wr,er = select([stdin], [], [], 0.01)
                if rd != []:
                    char = as_string(stdin.read(1))
            except KeyboardInterrupt:
                # Pass along a CTRL-C interrupt.
                raise
            except:
                pass
        return char

    def getch_noblock(stdin):
        """ Read one character from stdin without blocking.  Does not echo the
        character.  If no character is available, an empty string is returned.
        """
        char = ''

        # Using non-blocking read
        noncanonical_mode(stdin)

        try:
            # On OSX, calling read when no data is available causes the
            # file handle to never return any future data, so we need to
            # use select to make sure there is at least one char to read.
            rd,wr,er = select([stdin], [], [], 0.01)
            if rd != []:
                char = as_string(stdin.read(1))
        except KeyboardInterrupt:
            # Pass along a CTRL-C interrupt.
            raise
        except:
            pass

        # Convert linefeeds to carriage returns.
        if len(char) and ord(char) == 10:
            char = '\r'
        return char


def line_input(prompt='', stdin=sys.stdin, stdout=sys.stdout):
    """ Read a line from stdin, printing each character as it is typed.
    Does not echo a newline at the end.  This allows the calling program
    to overwrite the line by first sending a carriage return ('\r'), which
    is useful in modes like the interactive assembler.
    """
    stdout.write(prompt)
    stdout.flush()
    line = ''
    while True:
        char = getch(stdin)
        code = ord(char)
        if char in ("\n", "\r"):
            break
        elif code in (0x7f, 0x08):  # backspace
            if len(line) > 0:
                line = line[:-1]
                stdout.write("\r%s\r%s%s" %
                             (' ' * (len(prompt + line) + 5), prompt, line))
                stdout.flush()
        elif code == 0x1b:  # escape
            pass
        else:
            line += char
            stdout.write(char)
            stdout.flush()
    return line
