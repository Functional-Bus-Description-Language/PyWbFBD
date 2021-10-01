BUS_WIDTH = {Bus Width}

class StatusSingle:
    def __init__(self, interface, base_addr, registers):
        self.interface = interface

        if len(regs) == 1:
            self.mask = ((1 << (self.regs[0][1][0] + 1)) - 1) ^ ((1 << self.regs[0][1][1]) - 1)
        else:
            self.mask = ((1 << (self.regs[-1][1][0] + 1)) - 1) ^ ((1 << self.regs[-1][1][1]) - 1)

    def read(self):
        if len(regs) == 1:
            return (interface.read(regs[0][0]) & self.masks[0]) >> self.regs[0][1][1]
        else:
            raise Exception("TODO Implement")


{Code}
