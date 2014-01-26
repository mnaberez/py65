import sys

if sys.platform[:3] == "win":
    import msvcrt

    def getch(stdin):
        """ Read one character from the Windows console, blocking until one
        is available.  Does not echo the character.  The stdin argument is
        for function signature compatibility and is ignored.
        """
        return msvcrt.getch()

    def getch_noblock(stdin):
        """ Read one character from the Windows console without blocking.
        Does not echo the character.  If no character is available, an
        emptry string is returned.
        """
        if msvcrt.kbhit():
            return msvcrt.getch()
        return ''

else:
    import select
    import os
    import termios
    import fcntl

    def getch(stdin):
        """ Read one character from stdin, blocking until one is available.
        Does not echo the character.
        """
        fd = stdin.fileno()
        oldattr = termios.tcgetattr(fd)
        newattr = oldattr[:]
        newattr[3] &= ~termios.ICANON & ~termios.ECHO
        try:
            termios.tcsetattr(fd, termios.TCSANOW, newattr)
            char = stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldattr)
        return char

    def getch_noblock(stdin):
        """ Read one character from stdin without blocking.  Does not echo the
        character.  If no character is available, an empty string is returned.
        """

        fd = stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = oldterm[:]
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        try:
            char = ''
            r, w, e = select.select([fd], [], [], 0.1)
            if r:
                char = stdin.read(1)
                if char == "\n":
                    char = "\r"
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
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
