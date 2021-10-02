import math
from pprint import pprint
import os

from .. import utils

BUS_WIDTH = None

cmd_line_args = None
output_path = None


def generate(bus, cmd_line_args_):
    global BUS_WIDTH
    BUS_WIDTH = bus['main']['Properties']['width']

    global cmd_line_args
    cmd_line_args = cmd_line_args_

    global output_path
    if '--path' in cmd_line_args['python']:
        output_path = cmd_line_args['python']['--path'] + '/'
    else:
        output_path = cmd_line_args['global']['--path'] + '/python/'

    os.makedirs(output_path, exist_ok=True)

    template = utils.read_template('python/wbfbd.py')
    formatters = {'Bus Width': BUS_WIDTH}

    formatters['Code'] = generate_class('main', bus['main'])

    file_path = output_path + 'wbfbd.py'
    with open(file_path, 'w') as f:
        f.write(template.format(**formatters))


indent = ''

def increase_indent(val=1):
    global indent
    indent += val * '    '


def decrease_indent(val=1):
    global indent
    indent = indent[:val * (-4)]


def generate_class(name, element):
    count = element.get('Count', 1)
    base_addr = element['Address Space'][count - 1][0]

    code = indent + f"class class_{name}:\n"
    increase_indent()
    code += indent + "def __init__(self, interface):\n"
    increase_indent()
    #code += indent + "self.interface = interface\n"

    code += generate_statuses(element, base_addr)

    return code


def generate_statuses(element, base_addr):
    global indent

    code = ''

    for name, elem in element['Elements'].items():
        if elem['Base Type'] != 'status':
            continue

        count = elem.get('Count')
        strategy = elem['Access']['Strategy']
        mask = elem['Access']['Mask']
        addr = elem['Access']['Address']
        if count is None and strategy == 'Single':
            code += indent + f"self.{name} = StatusSingleSingle(interface, {base_addr + addr}, {mask})\n"
        if count is not None and strategy == 'Single':
            code += indent + f"self.{name} = StatusArraySingle(interface, {base_addr + addr}, {mask}, {count})\n"

    return code


def apply_base_addr(registers, base_addr):
    if type(registers) == tuple:
        pass
