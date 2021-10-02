BUS_WIDTH = {Bus Width}

class StatusSingleSingle:
    def __init__(self, interface, base_addr, addr, mask):
        self.interface = interface
        self.addr = base_addr + addr
        self.mask = ((1 << (mask[0] + 1)) - 1) ^ ((1 << mask[1]) - 1)
        self.shift = mask[1]

    def read(self):
        return (self.interface.read(self.addr) & self.mask) >> self.shift


{Code}
