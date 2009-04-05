import unittest
import sys
import re
import os
from py65.memory import ObservableMemory

class ObservableMemoryTests(unittest.TestCase):

    # __setitem__

    def test___setitem__with_no_listeners_changes_memory(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
 
        mem[0xC000] = 0xAB
        self.assertEqual(0xAB, subject[0xC000])
 
    def test___setitem__ignores_listeners_returning_none(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)

        def listener_1(address, value):
            return None

        def listener_2(address, value):
            return None
        
        mem.register_listener([0xC000], listener_1)
        mem.register_listener([0xC000], listener_2)
        
        mem[0xC000] = 0xAB
        self.assertEqual(0xAB, subject[0xC000])

    def test___setitem__uses_result_of_last_listener(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)

        def listener_1(address, value):
            return 0x01

        def listener_2(address, value):
            return 0x02
        
        mem.register_listener([0xC000], listener_1)
        mem.register_listener([0xC000], listener_2)
        
        mem[0xC000] = 0xAB
        self.assertEqual(0x02, subject[0xC000])

    # register_listener

    def test_register_listener_covers_all_addresses_in_range(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)

        def listener(address, value):
            return 0xAB
        
        mem.register_listener(xrange(0xC000, 0xC001+1), listener)

        mem[0xC000] = 0xAB
        mem[0xC001] = 0xAB
        self.assertEqual(0xAB, subject[0xC001])
        self.assertEqual(0xAB, subject[0xC001])

    def test_register_listener_does_not_register_same_listener_twice(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
        
        calls = []
        def listener(address, value):
            calls.append('listener')
        
        mem.register_listener([0xC000], listener)
        mem.register_listener([0xC000], listener)

        mem[0xC000] = 0xAB
        self.assertEqual(['listener'], calls)
   
    # __getitem__
    
    def test___getitem__with_no_providers_changes_memory(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
 
        subject[0xC000] = 0xAB
        self.assertEqual(0xAB, mem[0xC000])

    def test___getitem__ignores_providers_returning_none(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)

        def provider_1(address):
            return None

        def provider_2(address):
            return None
        
        mem.register_provider([0xC000], provider_1)
        mem.register_provider([0xC000], provider_2)
        
        mem[0xC000] = 0xAB
        self.assertEqual(0xAB, subject[0xC000])

    def test___getitem__calls_all_providers_and_uses_result_of_last(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
        
        calls = []
        def provider_1(address):
            calls.append('provider_1')
            return 0x01

        def provider_2(address):
            calls.append('provider_2')
            return 0x02
        
        mem.register_provider([0xC000], provider_1)
        mem.register_provider([0xC000], provider_2)

        subject[0xC000] = 0xAB
        self.assertEqual(0x02, mem[0xC000])
        self.assertEqual(['provider_1', 'provider_2'], calls)

    # __getattr__

    def test__getattr__proxies_subject(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
        self.assertEqual(subject.count, mem.count)

    # write
    
    def test_write_directly_writes_values_to_subject(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)

        def listener(address, value):
            return 0xFF
        mem.register_listener([0xC000,0xC001], listener)
        
        mem.write(0xC000, [0x01, 002])
        self.assertEqual(0x01, subject[0xC000])
        self.assertEqual(0x02, subject[0xC001])

    # Test Helpers
    
    def _make_subject(self):    
        subject = 0x10000 * [0x00] 
        return subject

