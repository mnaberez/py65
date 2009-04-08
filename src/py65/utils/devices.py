
def make_instruction_decorator(instruct, cycletime, extracycles):
    def instruction(opcode, opcycles, opextracycles=0):
        def decorate(f):
            instruct[opcode] = f
            cycletime[opcode] = opcycles
            extracycles[opcode] = opextracycles
            return f # Return the original function
        return decorate
    return instruction
