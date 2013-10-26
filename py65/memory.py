from collections import defaultdict


class ObservableMemory:
    def __init__(self, subject=None, addrWidth=16):
        self.physMask = 0xffff
        if addrWidth > 16:
            # even with 32-bit address space, model only 256k memory
            self.physMask = 0x3ffff

        if subject is None:
            subject = (self.physMask + 1) * [0x00]
        self._subject = subject

        self._read_subscribers = defaultdict(list)
        self._write_subscribers = defaultdict(list)

    def __setitem__(self, address, value):
        if isinstance(address, slice):
            r = range(*address.indices(self.physMask + 1))
            for n, v in zip(r, value):
                self[n] = v
            return

        address &= self.physMask
        callbacks = self._write_subscribers[address]

        for callback in callbacks:
            result = callback(address, value)
            if result is not None:
                value = result

        self._subject[address] = value

    def __getitem__(self, address):
        if isinstance(address, slice):
            r = range(*address.indices(self.physMask + 1))
            return [ self[n] for n in r ]

        address &= self.physMask
        callbacks = self._read_subscribers[address]
        final_result = None

        for callback in callbacks:
            result = callback(address)
            if result is not None:
                final_result = result

        if final_result is None:
            return self._subject[address]
        else:
            return final_result

    def __getattr__(self, attribute):
        return getattr(self._subject, attribute)

    def subscribe_to_write(self, address_range, callback):
        for address in address_range:
            address &= self.physMask
            callbacks = self._write_subscribers.setdefault(address, [])
            if callback not in callbacks:
                callbacks.append(callback)

    def subscribe_to_read(self, address_range, callback):
        for address in address_range:
            address &= self.physMask
            callbacks = self._read_subscribers.setdefault(address, [])
            if callback not in callbacks:
                callbacks.append(callback)

    def write(self, start_address, bytes):
        start_address &= self.physMask
        self._subject[start_address:start_address + len(bytes)] = bytes
