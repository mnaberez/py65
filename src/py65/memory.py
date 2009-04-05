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
        self._subject[address] = value
        
    def __getitem__(self, address):
        callbacks = self._providers[address]
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

    def register_listener(self, address_range, callback):
        for address in address_range:
            if not callback in self._listeners[address]:
                self._listeners[address].append(callback)

    def register_provider(self, address_range, callback): 
        for address in address_range:
            if not callback in self._providers[address]:
                self._providers[address].append(callback)

    def write(self, start_address, bytes):
        self._subject[start_address:start_address+len(bytes)] = bytes
