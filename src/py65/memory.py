from collections import defaultdict

class ObservableMemory:
    def __init__(self, subject=None):
        if subject is None:
            subject = 0x10000 * [0x00]
        self._subject = subject

        self._read_subscribers  = defaultdict(list)
        self._write_subscribers = defaultdict(list)        

    def __setitem__(self, address, value):
        callbacks = self._write_subscribers[address]

        for callback in callbacks:
            result = callback(address, value)
            if result is not None:
                value = result

        self._subject[address] = value
        
    def __getitem__(self, address):
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
            if not callback in self._write_subscribers[address]:
                self._write_subscribers[address].append(callback)

    def subscribe_to_read(self, address_range, callback): 
        for address in address_range:
            if not callback in self._read_subscribers[address]:
                self._read_subscribers[address].append(callback)

    def write(self, start_address, bytes):
        self._subject[start_address:start_address+len(bytes)] = bytes
