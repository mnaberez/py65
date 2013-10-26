from binascii import a2b_hex


def load(text):
    load = Loader(text)
    return (load.start_address, load.data)


class Loader:
    def __init__(self, text):
        self.load(text)

    def load(self, text):
        self._reset()

        for line in text.splitlines():
            self._parse_line(line)

    def _reset(self):
        self.data = []
        self.start_address = None
        self.current_address = None

    def _parse_line(self, line):
        line = self._remove_comments(line)
        pieces = line.strip().split()

        for piece in pieces:
            if piece.startswith('$'):
                piece = piece[1:]

            if piece.endswith(':'):
                self._parse_address(piece[:-1])

            else:
                self._parse_bytes(piece)

    def _remove_comments(self, line):
        for delimiter in (';', '--', '#'):
            pos = line.find(delimiter)
            if pos != -1:
                line = line[:pos]
        return line

    def _parse_address(self, piece):
        try:
            binstr = a2b_hex(piece.encode('utf-8'))
            if isinstance(binstr, str):
                addr_bytes = [ ord(b) for b in binstr ]
            else: # Python 3
                addr_bytes = [ b for b in binstr ]
        except (TypeError, ValueError):
            msg = "Could not parse address: %s" % piece
            raise ValueError(msg)

        if len(addr_bytes) != 2:
            msg = "Expected address to be 2 bytes, got %d" % (
                  len(addr_bytes))
            raise ValueError(msg)

        address = (addr_bytes[0] << 8) + addr_bytes[1]

        if self.start_address is None:
            self.start_address = address
            self.current_address = address

        elif address != (self.current_address):
            msg = "Non-contigous block detected.  Expected next address " \
                  "to be $%04x, label was $%04x" % (self.current_address,
                                                    address)
            raise ValueError(msg)

    def _parse_bytes(self, piece):
        if self.start_address is None:
            msg = "Start address was not found in data"
            raise ValueError(msg)

        else:
            try:
                binstr = a2b_hex(piece.encode('utf-8'))
                if isinstance(binstr, str):
                    data_bytes = [ ord(b) for b in binstr ]
                else: # Python 3
                    data_bytes = [ b for b in binstr ]
            except (TypeError, ValueError):
                msg = "Could not parse data: %s" % piece
                raise ValueError(msg)

            self.current_address += len(data_bytes)
            self.data.extend(data_bytes)
