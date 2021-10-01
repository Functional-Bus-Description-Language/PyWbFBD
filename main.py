#!/bin/python3
VERSION = "0.0.0"

import time

import fbdl
import yaml

from wbfbd import args
from wbfbd.python import python
from wbfbd.vhdl import vhdl


def main():
    cmd_line_args = args.parse(VERSION)

    start_time_in_ms = int(time.time() * 1000)
    bus = fbdl.compile(cmd_line_args['main'])
    compile_time_in_ms = int(time.time() * 1000)

    if 'vhdl' in cmd_line_args:
        vhdl.generate(bus, cmd_line_args)

    if 'python' in cmd_line_args:
        python.generate(bus, cmd_line_args)

    if '--fusesoc' in cmd_line_args['global']:
        generate_fusesoc_core_file(cmd_line_args)

    generate_time_in_ms = int(time.time() * 1000)
    if '--times' in cmd_line_args['global']:
        print_times(start_time_in_ms, compile_time_in_ms, generate_time_in_ms)


def generate_fusesoc_core_file(cmd_line_args):
    with open('./wbfbd_main.core', 'w') as f:
        f.write('CAPI=2:\n')

        coredata = {
            'name': cmd_line_args['global']['--fusesoc-vlnv'],
            'targets': {'default': {}},
        }

        coredata['filesets'] = {
            'vhdl': {
                'files': vhdl.generated_files,
                'file_type': 'vhdlSource-2008',
                'logical_name': 'wbfbd',
            }
        }
        coredata['targets']['default']['filesets'] = ['vhdl']

        f.write(yaml.dump(coredata))


def print_times(start_time_in_ms, compile_time_in_ms, generate_time_in_ms):
    print(f"Compile time: {compile_time_in_ms - start_time_in_ms} ms.")
    print(f"Generate time: {generate_time_in_ms - compile_time_in_ms} ms.")


if __name__ == "__main__":
    main()
