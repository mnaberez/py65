import sys

if sys.platform[:3] == "win":
    import msvcrt

    def getch_noblock(stdin):
        """ Performs a nonblocking read of one character from the Windows
        console and returns it.  The stdin argument is for function 
        signature compatibility and is ignored.  If no character is 
        available, an empty string is returned.
        """
        if msvcrt.kbhit():
            return msvcrt.getch()
        return ''

else:
    import select
    import os
    import termios
    import fcntl

    def getch_noblock(stdin):
        """ Performs a nonblocking read of one character from stdin  
        returns it.  If no character is available, an empty string 
        is returned.
        """
    
        fd = stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = oldterm[:]
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        try:
            byte = 0
            r, w, e = select.select([fd], [], [], 0.1)
            if r:
                char = stdin.read(1)
                if char == "\n":
                    char = "\r" 
            else:
              char = ''
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        return char
