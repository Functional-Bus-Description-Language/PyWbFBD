import math
import os

from .. import utils

from . import status

BUS_WIDTH = None

cmd_line_args = None
output_path = None

generated_files = []

def generate(bus, cmd_line_args_):
    global BUS_WIDTH
    BUS_WIDTH = bus['main']['Properties']['width']

    global cmd_line_args
    cmd_line_args = cmd_line_args_

    global output_path
    if '--path' in cmd_line_args['vhdl']:
        output_path = cmd_line_args['vhdl']['--path'] + '/'
    else:
        output_path = cmd_line_args['global']['--path'] + '/vhdl/'

    os.makedirs(output_path, exist_ok=True)

    generate_wbfbd_package(bus['main'])

    entities = collect_entities(bus['main'])

    resolve_entity_name_conflicts(entities)

    for entity in entities:
        generate_entity(entity['Name'], entity['Entity'])


def collect_entities(element, entities=None, path=None):
    """Collect entities that should be generated."""
    if not entities:
        entities = [{'Name': 'main', 'Path': 'main', 'Entity': element}]
        path = ['main']
    else:
        item = {'Name': path[-1], 'Path': '_'.join(path), 'Entity': element}
        entities.append(item)

    for name, elem in element['Elements'].items():
        if elem['Base Type'] == 'block':
            path.append(name)
            entities = collect_entities(elem, entities, path)
            path.pop(-1)

    return entities


def resolve_entity_name_conflicts(entities):
    for i, e1 in enumerate(entities[:-1]):
        conflicts = [e2 for e2 in entities[i + 1:] if e2['Name'] == e1['Name']]
        conflicts.append(e1)

        if len(conflicts) == 1:
            continue

        paths = [e['Path'].split('_') for e in conflicts]
        lengths = [len(path) for path in paths]
        max_length = max(lengths)
        new_names = [e['Name'] for e in conflicts]
        for j in range(2, max_length):
            new_names = ['_'.join(path[-j:]) if j <= len(path) else '_'.join(path) for path in paths]
            if len(new_names) == len(set(new_names)):
                break

        for i, e in enumerate(conflicts):
            e['Name'] = new_names[i]


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
        'Constants': generate_constants(block),
        'Entity Subblock Ports': '',
        'Entity Functional Ports': '',
        'Crossbar Subblock Ports': '',
        'Signal Declarations': '',
        'Address Values': '',
        'Mask Values': '',
        'Number of Subblocks': 0,
        'Statuses Access': '-- Statuses access.\n',
        'Statuses Routing': '-- Statuses routing.\n',
        'Default Values': '',
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

    default_values = {}
    for name, elem in block['Elements'].items():
        if elem['Base Type'] == 'status':
            status.generate(name, elem, formatters, default_values)

    compose_default_values(formatters, default_values)

    file_path = output_path + f'{block_name}.vhd'
    with open(file_path, 'w', encoding='latin-1') as f:
        f.write(block_template.format(**formatters))
    generated_files.append(file_path)


def generate_block(name, elem, num_of_addr_bits, current_subblock_addr, formatters):
    count = elem.get('Count', 1)
    initial_num_of_subblocks = formatters['Number of Subblocks']

    formatters[
        'Entity Subblock Ports'
    ] += f";\n      {name}_master_o : out t_wishbone_master_out_array({count - 1} downto 0)"
    formatters[
        'Entity Subblock Ports'
    ] += f";\n      {name}_master_i : in  t_wishbone_master_in_array ({count - 1} downto 0)"

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


def generate_wbfbd_package(bus):
    template = utils.read_template('vhdl/wbfbd.vhd', 'latin-1')

    file_path = output_path + 'wbfbd.vhd'
    with open(file_path, 'w', encoding='latin-1') as f:
        f.write(template)
    generated_files.append(file_path)


def generate_constants(element):
    code = ''

    if 'Constants' in element:
        for name, val in element['Constants'].items():
            name.upper()
            if not name.startswith('C_'):
                name = 'C_' + name

            type_ = type(val)
            if type_ == int:
                declaration = f"   constant {name} : integer := {val};\n"
            elif type_ == list:
                inner_type = type(val[0])
                if inner_type == int:
                    declaration = f"   constant {name} : t_integer_vector := ("
                    for i, v in enumerate(val):
                        declaration += f"{i} => {v}, "
                    declaration = declaration[:-2]
                    declaration += ");\n"
                else:
                    raise Exception(f"{inner_type} not implemented.")
            else:
                raise Exception(f"{type_} not implemented.")

            code += declaration

    return code


def compose_default_values(formatters, default_values):
    code = ''
    for addr, values in default_values.items():
        code += f'{addr} => ('
        for v in values:
            width = v[1][0] - v[1][1] + 1
            code += f'{v[1][0]} downto {v[1][1]} => "{v[0]:0{width}b}", '
        code = code[:-2]
        code += '), '

    formatters['Default Values'] += code
