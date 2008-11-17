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
        for oper, addr_range, callback in self._observers:
            if address in addr_range:
                if (oper == self.RW) or (oper == self.WRITE):
                    result = callback(self.WRITE, address, value)        
                    if result is not None:
                        value = result
        self._subject[address] = value

    def __getitem__(self, address):
        for oper, addr_range, callback in self._observers:
            if address in addr_range:
                if (oper == self.RW) or (oper == self.READ):
                    result = callback(self.READ, address, None)
                    if result is not None:
                        return result
        return self._subject[address]
    
    def __getattr__(self, address):
        return getattr(self._subject, address)

    def subscribe(self, operation, addr_range, callback):
        if operation not in (self.READ, self.WRITE, self.RW):
            raise ValueError("Unsupported operation")
        self._observers.append([operation, addr_range, callback])

    def dma_read(self, key):
        return self._subject[key]
    
    def dma_write(self, key, value):
        self._subject[key] = value
