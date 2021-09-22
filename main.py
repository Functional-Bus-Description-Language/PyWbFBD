#!/bin/python3

import argparse

VERSION = "0.0.0"


def parse_cmd_line_args():
    parser = argparse.ArgumentParser(
        prog='wbfbd',
        description="Functional Bus Description Language compiler back-end for Wishbone written in Python.",
    )

    parser.add_argument(
        '-v', '--version', help="Display version.", action="version", version=VERSION
    )

    parser.add_argument('main', help="Path to the main file.")

    parser.add_argument('-d', help="Log debug messages.", action='store_true')

    return parser.parse_args()


def main():
    cmd_line_args = parse_cmd_line_args()

if __name__ == "__main__":
    main()
