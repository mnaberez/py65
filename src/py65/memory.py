from collections import defaultdict

class ObservableMemory:
    def __init__(self, subject=None):
        if subject is None:
            subject = 0x10000 * [0x00]
        self._subject = subject

        self._listeners = defaultdict(list)
        self._providers = defaultdict(list)        

    def __setitem__(self, address, value):
        callbacks = self._listeners[address]
        for callback in callbacks:
            result = callback(address, value)
            if result is not None:
                value = result

    def __getitem__(self, address):
        callbacks = self._providers[address]
        final_result = None

        for callback in callbacks:
            result = callback(address)
            if result is not None:
                final_result = result

        if final_result:
            return final_result
        else:
            return self._subject[address]
    
    def __getattr__(self, address):
        return getattr(self._subject, address)

    def register_provider(self, address_range, callback):
        for address in address_range:
            self._providers[address].append(callback)

    def register_listener(self, address_range, callback):
        for address in address_range:
            self._listeners[address].append(callback)

    def write(self, start_address, bytes):
        self._subject[start_address:start_address+len(bytes)] = bytes
