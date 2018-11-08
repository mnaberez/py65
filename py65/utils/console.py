import sys
import time

if sys.platform[:3] == "win":
    import msvcrt

    def noncanonical_mode(stdin):
        """ noncanonical_mode is a no-op on Windows. """
        return

    def restore_mode(stdin):
        """ restore_mode is a no-op on Windows. """
        return

    def getch(stdin):
        """ Read one character from the Windows console, blocking until one
        is available.  Does not echo the character.  The stdin argument is
        for function signature compatibility and is ignored.
        """
        c = msvcrt.getch()
        if isinstance(c, bytes): # Python 3
            c = c.decode('latin-1')
        return c

    def getch_noblock(stdin):
        """ Read one character from the Windows console without blocking.
        Does not echo the character.  The stdin argument is for function
        signature compatibility and is ignored.  If no character is
        available, an empty string is returned.
        """
        if msvcrt.kbhit():
            return getch(stdin)
        return ''

else:
    import select
    import os
    import termios
    import fcntl

    oldattr_stack = [ ]


    def noncanonical_mode(stdin):
        """For operating systems that support it, switch to noncanonical
        mode.  In this mode, characters are given immediately to the
        program and no processing of editing characters (like backspace)
        is performed.  Echo is also turned off in this mode.  The
        previous input behavior can be restored with restore_mode.
        """
        # For non-windows systems, switch to non-canonical
        # and no-echo non-blocking-read mode.

        global oldattr_stack

        # Save the current terminal setup.
        fd = stdin.fileno()
        oldattr = termios.tcgetattr(fd)
        oldattr_stack.append(oldattr)
        
        # Switch to noncanonical (instant) mode with no echo.
        newattr = oldattr[:]
        newattr[3] &= ~termios.ICANON & ~termios.ECHO

        # Switch to non-blocking reads with 0.1 second timeout.
        newattr[6][termios.VMIN] = 0
        newattr[6][termios.VTIME] = 1
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

    def restore_mode(stdin):
        """For operating systems that support it, restore the previous 
        input mode.
        """

        # Restore the previous input setup.
        global oldattr_stack
        fd = stdin.fileno()
        # If there is a previous setting, restore it.
        if oldattr_stack:
            termios.tcsetattr(fd, termios.TCSANOW, oldattr_stack.pop())



    def getch(stdin):
        """ Read one character from stdin, blocking until one is available.
        Does not echo the character.
        """
        # Try to get a character with a non-blocking read.
        char = ''
        noncanonical_mode(stdin)
        while char == '':
            char = stdin.read(1)
        restore_mode(stdin)
        return char

    def getch_noblock(stdin):
        """ Read one character from stdin without blocking.  Does not echo the
        character.  If no character is available, an empty string is returned.
        """
        char = ''

        # Using non-blocking read as set up in Monitor._run
        noncanonical_mode(stdin)
        char = stdin.read(1)
        restore_mode(stdin)

        if char == "\n":
            char = "\r"
        return char


def line_input(prompt='', stdin=sys.stdin, stdout=sys.stdout):
    """ Read a line from stdin, printing each character as it is typed.
    Does not echo a newline at the end.  This allows the calling program
    to overwrite the line by first sending a carriage return ('\r'), which
    is useful in modes like the interactive assembler.
    """
    stdout.write(prompt)
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
        elif code == 0x1b:  # escape
            pass
        else:
            line += char
            stdout.write(char)
            stdout.flush()
    return line
