#!/bin/python3
VERSION = "0.0.0"

import fbdl

from wbfbd import args


def main():
    cmd_line_args = args.parse(VERSION)

    bus = fbdl.compile(cmd_line_args['main'])


if __name__ == "__main__":
    main()
