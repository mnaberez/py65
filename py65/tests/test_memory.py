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
 
    def test___setitem__ignores_subscribers_returning_none(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)

        def write_subscriber_1(address, value):
            return None

        def write_subscriber_2(address, value):
            return None
        
        mem.subscribe_to_write([0xC000], write_subscriber_1)
        mem.subscribe_to_write([0xC000], write_subscriber_2)
        
        mem[0xC000] = 0xAB
        self.assertEqual(0xAB, subject[0xC000])

    def test___setitem__uses_result_of_last_subscriber(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
    
        def write_subscriber_1(address, value):
            return 0x01
    
        def write_subscriber_2(address, value):
            return 0x02
        
        mem.subscribe_to_write([0xC000], write_subscriber_1)
        mem.subscribe_to_write([0xC000], write_subscriber_2)
        
        mem[0xC000] = 0xAB
        self.assertEqual(0x02, subject[0xC000])
     
    # subscribe_to_read
    
    def test_subscribe_to_read_covers_all_addresses_in_range(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
    
        def read_subscriber(address, value):
            return 0xAB
        
        mem.subscribe_to_read(xrange(0xC000, 0xC001+1), read_subscriber)
    
        mem[0xC000] = 0xAB
        mem[0xC001] = 0xAB
        self.assertEqual(0xAB, subject[0xC001])
        self.assertEqual(0xAB, subject[0xC001])
     
    def test__subscribe_to_read_does_not_register_same_listener_twice(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
        
        calls = []
        def read_subscriber(address):
            calls.append('read_subscriber')
        
        mem.subscribe_to_read([0xC000], read_subscriber)
        mem.subscribe_to_read([0xC000], read_subscriber)
    
        value = mem[0xC000]
        self.assertEqual(['read_subscriber'], calls)
       
    # __getitem__
    
    def test___getitem__with_no_write_subscribers_changes_memory(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
     
        subject[0xC000] = 0xAB
        self.assertEqual(0xAB, mem[0xC000])
       
    def test___getitem__ignores_read_subscribers_returning_none(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
    
        def read_subscriber_1(address):
            return None
    
        def read_subscriber_2(address):
            return None
        
        mem.subscribe_to_read([0xC000], read_subscriber_1)
        mem.subscribe_to_read([0xC000], read_subscriber_2)
        
        mem[0xC000] = 0xAB
        self.assertEqual(0xAB, subject[0xC000])
        
    def test___getitem__calls_all_read_subscribers_uses_last_result(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
        
        calls = []
        def read_subscriber_1(address):
            calls.append('read_subscriber_1')
            return 0x01
    
        def read_subscriber_2(address):
            calls.append('read_subscriber_2')
            return 0x02
        
        mem.subscribe_to_read([0xC000], read_subscriber_1)
        mem.subscribe_to_read([0xC000], read_subscriber_2)
    
        subject[0xC000] = 0xAB
        self.assertEqual(0x02, mem[0xC000])

        expected_calls = ['read_subscriber_1', 'read_subscriber_2']
        self.assertEqual(expected_calls, calls)
     
    # __getattr__
    
    def test__getattr__proxies_subject(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
        self.assertEqual(subject.count, mem.count)
    
    # write
    
    def test_write_directly_writes_values_to_subject(self):
        subject = self._make_subject()
        mem = ObservableMemory(subject=subject)
    
        def write_subscriber(address, value):
            return 0xFF
        mem.subscribe_to_write([0xC000,0xC001], write_subscriber)
        
        mem.write(0xC000, [0x01, 002])
        self.assertEqual(0x01, subject[0xC000])
        self.assertEqual(0x02, subject[0xC001])

    # Test Helpers
    
    def _make_subject(self):    
        subject = 0x10000 * [0x00] 
        return subject

if __name__ == '__main__':
    unittest.main()
