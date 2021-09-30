"""
Custom module for arguments parsing.
argparse is not handy in this particular case.
"""
import sys
from pprint import pformat


valid_targets = {
    'python': {
        'Flags': {
            '--help': "Display help.",
            '--no-asserts': "Do not include asserts. Not yet implemented.",
        },
        'Options': {'--path': "Path for output files."},
    },
    'vhdl': {
        'Flags': {
            '--help': "Display help.",
            '--no-psl': "Do not include PSL assertions. Not yet implemented.",
        },
        'Options': {'--path': "Path for output files."},
    },
}


HELP = """Functional Bus Description Language compiler back-end for Wishbone written in Python.
Version {version}.

Supported targets:"""
for i, target in enumerate(valid_targets):
    if i > 0:
        HELP += ', '
    else:
        HELP += ' '
    HELP += target
HELP += """.\nTo check valid flags and options for a given target type: 'wbfbd {{target}} --help'.

Usage:
  wbfbd [{{target}} [target flag or option] ...] ... path/to/fbd/file/with/main/bus/

  At least one target must be specified. The last argument is always a path
  to the fbd file containing a definition for the main bus, unless it is
  '-h', '--help', '-v' or '--version.'

Flags:
  -h, --help     Display help.
  -v, --version  Display version.
  --fusesoc  Generate FuseSoc '.core' file.
             This flag rather should not be set manually.
             It is recommended to use wbfbd as a generator inside FuseSoc.
             All necessary files can be found in the 'FuseSoc' directory in the wbfbd repository.
  --times  Print compile and generate times.

Options:
  --fusesoc-vlnv  FuseSoc VLNV tag.
  --path  Path for target directories with output files.
          The default is 'wbfbd' directory in the current working directory."""


def print_target_help(target):
    if not valid_targets[target]['Flags'] and not valid_targets[target]['Options']:
        print(f"Target '{target}' does not have any flags or options.")
        exit(0)

    print(f"wbfbd help for '{target}' target.\n")
    if valid_targets[target]['Flags']:
        print("Flags:")
        for flag, desc in valid_targets[target]['Flags'].items():
            print(f"  {flag: <{8}} {desc}")

    if valid_targets[target]['Options']:
        print("\nOptions:")
        for opt, desc in valid_targets[target]['Options'].items():
            print(f"  {opt: <{8}} {desc}")

    exit(0)


def parse(version):
    if len(sys.argv) == 1:
        raise Exception("Missing target and main file.")

    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ['-h', '--help']:
            print(HELP.format(version=version))
            exit(0)
        elif arg in ['-v', '--version']:
            print(version)
            exit(0)
        else:
            if arg in valid_targets:
                raise Exception("No main file has been specified.")
            else:
                raise Exception(f"'{arg}' is not a valid target.\n")

    cmd_line_args = {'global': {}}
    current_target = None
    current_option = None
    expect_argument = False

    in_global_args = True

    for i, arg in enumerate(sys.argv[1:]):
        if i == len(sys.argv) - 2:
            if not arg.startswith('-'):
                break

        if in_global_args:
            if arg in ['-h', '--help']:
                print(HELP.format(version=version))
                exit(0)
            elif arg in ['-v', '--version']:
                print(version)
                exit(0)
            elif expect_argument:
                cmd_line_args['global'][current_option] = arg
                expect_argument = False
            elif arg in ['--fusesoc', '--times']:
                cmd_line_args['global'][arg] = True
            elif arg in ['--fusesoc-vlnv', '--path']:
                current_option = arg
                expect_argument = True
            elif arg[0] != '-':
                in_global_args = False
                if arg not in valid_targets:
                    raise Exception(f"'{arg}' is not a valid target.\n")
                current_target = arg
                cmd_line_args[arg] = {}
            else:
                raise Exception(f"Invalid option {arg}.")

            continue

        if expect_argument:
            cmd_line_args[current_target][current_option] = arg
            expect_argument = False
        elif arg in valid_targets:
            current_target = arg
            cmd_line_args[arg] = {}
            continue
        elif (
            arg not in valid_targets[current_target]['Options']
            and arg not in valid_targets[current_target]['Flags']
            and expect_argument == False
        ):
            raise Exception(
                f"'{arg}' is not a valid flag or option for '{current_target}' target.\n"
                + f"Run 'wbfbd {current_target} --help' to see valid flags and options."
            )
        elif arg in ['--help']:
            print_target_help(current_target)
        elif arg in valid_targets[current_target]['Flags']:
            # Use None as the value as any further checks will simply check if flag is in the dictionary.
            cmd_line_args[current_target][arg] = None
        elif arg in valid_targets[current_target]['Options']:
            # Use None as the value as any further checks will simply check if flag is in the dictionary.
            cmd_line_args[current_target][arg] = None
            current_option = arg
            expect_argument = True

    if expect_argument:
        raise Exception(
            f"Missing argument for '{current_option}' option, target '{current_target}'."
        )

    cmd_line_args['main'] = sys.argv[-1]

    # Default values handling.
    if '--path' not in cmd_line_args['global']:
        cmd_line_args['global']['--path'] = 'wbfbd'

    return cmd_line_args
