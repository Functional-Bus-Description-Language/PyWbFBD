#!/usr/bin/python3
"""
FuseSoc wrapper for wbfbd.
"""

import os
import sys
import yaml
import subprocess

if __name__ == "__main__":

    with open(sys.argv[1], 'r') as config_file:
        config = yaml.safe_load(config_file)

    files_root = config['files_root'] + "/"

    try:
        main = files_root + config['parameters']['main']
    except:
        print("ERROR: Input .fbd main file ('main' parameter) musts be specified!")
        sys.exit(1)

    args = ['wbfbd', '--fusesoc', '--fusesoc-vlnv', config['vlnv']]

    for param, val in config['parameters'].items():
        if param in ['global', 'main']:
            continue

        args.append(param)
        prev_v = None
        for v in val:
            if prev_v == '--path':
                args.append(files_root + v)
            else:
                args.append(v)
            prev_v = v

    args.append(main)

    ret = subprocess.run(args)
    if ret.returncode != 0:
        exit(ret.returncode)
