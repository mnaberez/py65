class ObservableMemory:
    READ  = 0
    WRITE = 1
    RW    = 2

    def __init__(self, subject=None):
        if subject is None:
            subject = []
            for addr in range(0x0000, 0xFFFF+1):
                subject.insert(addr, 0x00)
        self._subject = subject
        self._observers = []

    def __setitem__(self, address, value):
        self._notify(self.WRITE, address, value)
        self._subject[address] = value

    def __getitem__(self, address):
        self._notify(self.READ, address)
        return self._subject[address]
    
    def __getattr__(self, address):
        return getattr(self._subject, address)

    def _notify(self, operation, address, value=None):
        for oper, addr_range, callback in self._observers:
            if address in addr_range:
                if (oper == self.RW) or (oper == operation):
                    callback(operation, address, value)

    def subscribe(self, operation, addr_range, callback):
        if operation not in (self.READ, self.WRITE, self.RW):
            raise ValueError("Unsupported operation")
        self._observers.append([operation, addr_range, callback])

    def dma_read(self, key):
        return self._subject[key]
    
    def dma_write(self, key, value):
        self._subject[key] = value
