

def make_instruction_decorator(instruct, disasm, allcycles, allextras):
    def instruction(name, mode, cycles, extracycles=0):
        def decorate(f):
            opcode = int(f.__name__.split('_')[-1], 16)
            instruct[opcode] = f
            disasm[opcode] = (name, mode)
            allcycles[opcode] = cycles
            allextras[opcode] = extracycles
            return f  # Return the original function
        return decorate
    return instruction
