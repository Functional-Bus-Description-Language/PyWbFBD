#!/bin/python3
VERSION = "0.0.0"

import fbdl
import yaml

from wbfbd import args
from wbfbd.vhdl import vhdl


def main():
    cmd_line_args = args.parse(VERSION)

    bus = fbdl.compile(cmd_line_args['main'])

    if 'vhdl' in cmd_line_args:
        vhdl.generate(bus, cmd_line_args)

    if '--fusesoc' in cmd_line_args['global']:
        generate_fusesoc_core_file(cmd_line_args)


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


if __name__ == "__main__":
    main()
