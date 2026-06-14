"""Helpers for functional tests based on executing 65x02 object code."""


class FunctionalTestExecutor(object):
    def __init__(self, mpu_class, filename, load_addr):
        self.mpu_class = mpu_class
        self.mpu = self._make_mpu()

        object_code = bytearray(open(filename, "rb").read())
        self.write_memory(load_addr, object_code)

    def _make_mpu(self, *args, **kargs):
        mpu = self.mpu_class(*args, **kargs)
        if 'memory' not in kargs:
            mpu.memory = 0x10000 * [0xAA]
        return mpu

    def write_memory(self, start_address, bytes):
        self.mpu.memory[start_address:start_address + len(bytes)] = bytes

    @staticmethod
    def never_trace_predicate(pc):
        return False

    @staticmethod
    def always_trace_predicate(pc):
        return True

    @staticmethod
    def address_completion_predicate(addrs):
        """Terminate test when PC loops to itself or enters addrs set"""
        def completion_predicate(mpu, old_pc):
            return mpu.pc == old_pc or mpu.pc in addrs

        return completion_predicate

    def execute(
            self, pc, completion_predicate,
            trace_predicate=never_trace_predicate
    ):
        self.mpu.pc = pc

        while True:
            old_pc = self.mpu.pc
            self.mpu.step(trace=trace_predicate(self.mpu.pc))
            if completion_predicate(self.mpu, old_pc):
                break


def trace_on_assertion(executor, *args, **kwargs):
    try:
        return executor(*args, **kwargs)
    except AssertionError:
        # Rerun with tracing
        return executor(*args, trace=True, **kwargs)

