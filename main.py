#!/bin/python3
VERSION = "0.0.0"

import fbdl

from wbfbd import args
from wbfbd.vhdl import vhdl


def main():
    cmd_line_args = args.parse(VERSION)

    bus = fbdl.compile(cmd_line_args['main'])

    if 'vhdl' in cmd_line_args:
        vhdl.generate(bus, cmd_line_args)


if __name__ == "__main__":
    main()
