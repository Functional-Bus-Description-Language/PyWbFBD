import math
import os

from .. import utils

from . import status

BUS_WIDTH = None

cmd_line_args = None
output_path = None


def generate(bus, cmd_line_args_):
    global BUS_WIDTH
    BUS_WIDTH = bus['main']['Properties']['width']

    global cmd_line_args
    cmd_line_args = cmd_line_args_

    global output_path
    if '--path' in cmd_line_args['vhdl']:
        output_path = cmd_line_args['vhdl']['--path']
    else:
        output_path = cmd_line_args['global']['--path'] + '/vhdl/'

    os.makedirs(output_path, exist_ok=True)

    generate_wbfbd_package()

    generate_entity('main', bus['main'])


def generate_entity(block_name, block):
    block_template = utils.read_template('vhdl/block.vhd', 'latin-1')

    formatters = {
        'Bus Width': BUS_WIDTH,
        'Entity Name': block_name,
        'Number of Masters': block['Properties']['masters'],
        'Number of Registers': block['Sizes']['Own'],
        'Number of Internal Address Bits': math.ceil(
            math.log(block['Sizes']['Own'], 2)
        ),
        'Entity Subblock Ports': '',
        'Entity Functional Ports': '',
        'Crossbar Subblock Ports': '',
        'Signal Declarations': '',
        'Address Values': '',
        'Mask Values': '',
        'Number of Subblocks': 0,
        'Statuses Access': '-- Statuses access.\n',
        'Statuses Routing': '-- Statuses routing.\n',
        'Register Initial Values': '',
    }

    num_of_addr_bits = int(math.log(block['Sizes']['Block Aligned'], 2))

    subblocks = [
        (name, elem)
        for name, elem in block['Elements'].items()
        if elem['Base Type'] == 'block'
    ]
    subblocks.sort(key=lambda sb: sb[1]['Sizes']['Block Aligned'], reverse=True)

    formatters['Address Values'] += f'0 => "{0:032b}"'
    if not subblocks:
        mask = 0
    else:
        mask = ((1 << num_of_addr_bits) - 1) ^ (
            (1 << (math.ceil(math.log(block["Sizes"]["Own"], 2)))) - 1
        )
    formatters['Mask Values'] += f'{formatters["Number of Subblocks"]} => "{mask:032b}"'

    current_subblock_addr = block['Sizes']['Block Aligned']

    for name, sb in subblocks:
        current_subblock_addr = generate_block(
            name, sb, num_of_addr_bits, current_subblock_addr, formatters
        )

    for name, elem in block['Elements'].items():
        if elem['Base Type'] == 'status':
            status.generate(name, elem, formatters)

    file_path = output_path + f'/{block_name}.vhd'
    with open(file_path, 'w', encoding='latin-1') as f:
        f.write(block_template.format(**formatters))

    for name, sb in subblocks:
        generate_entity(name, sb)


def generate_block(name, elem, num_of_addr_bits, current_subblock_addr, formatters):
    count = elem.get('Count', 1)
    initial_num_of_subblocks = formatters['Number of Subblocks']

    formatters[
        'Entity Subblock Ports'
    ] += f";\n      {name}_master_o : out t_wishbone_master_out_array({count} - 1 downto 0)"
    formatters[
        'Entity Subblock Ports'
    ] += f";\n      {name}_master_i : in  t_wishbone_master_in_array ({count} - 1 downto 0)"

    if count == 1:
        formatters[
            'Crossbar Subblock Ports'
        ] += f",\n      master_i({initial_num_of_subblocks + 1}) => {name}_master_i"
        formatters[
            'Crossbar Subblock Ports'
        ] += f",\n      master_o({initial_num_of_subblocks + 1}) => {name}_master_o"
    else:
        lower_range = initial_num_of_subblocks + 1
        upper_range = lower_range + count - 1
        formatters[
            'Crossbar Subblock Ports'
        ] += f",\n      master_i({upper_range} downto {lower_range}) => {name}_master_i"
        formatters[
            'Crossbar Subblock Ports'
        ] += f",\n      master_o({upper_range} downto {lower_range}) => {name}_master_o"

    for i in range(count):
        formatters['Number of Subblocks'] += 1
        current_subblock_addr -= elem['Sizes']['Block Aligned']
        mask = ((1 << num_of_addr_bits) - 1) ^ (
            (1 << math.ceil(math.log(elem["Sizes"]["Own"], 2))) - 1
        )
        formatters[
            'Address Values'
        ] += f', {formatters["Number of Subblocks"]} => "{current_subblock_addr:032b}"'
        formatters[
            'Mask Values'
        ] += f', {formatters["Number of Subblocks"]} => "{mask:032b}"'

    return current_subblock_addr


def generate_wbfbd_package():
    template = utils.read_template('vhdl/wbfbd.vhd', 'latin-1')

    file_path = output_path + '/wbfbd.vhd'
    with open(file_path, 'w', encoding='latin-1') as f:
        f.write(template)
