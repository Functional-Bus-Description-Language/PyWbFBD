def generate(name, elem, formatters, default_values):
    if 'Count' in elem:
        generate_array(name, elem, formatters, default_values)
    else:
        generate_single(name, elem, formatters, default_values)


def generate_single(name, elem, formatters, default_values):
    if name not in ['x_uuid_x', 'x_timestamp_x']:
        formatters[
            'Entity Functional Ports'
        ] += f";\n      {name}_i : in std_logic_vector({elem['Properties']['width'] - 1} downto 0)"

    strategy = elem['Access']['Strategy']

    if strategy == 'Single':
        generate_single_single(name, elem, formatters, default_values)
    elif strategy == 'Linear':
        generate_single_linear(name, elem, formatters, default_values)


def generate_single_single(name, elem, formatters, default_values):
    addr = elem['Access']['Address']
    mask = elem['Access']['Mask']

    access = f"""
            {name} : if internal_addr = {addr} then
               internal_master_in.dat({mask[0]} downto {mask[1]}) <= registers(internal_addr)({mask[0]} downto {mask[1]});
"""

    routing = ''
    if name not in ['x_uuid_x', 'x_timestamp_x']:
        routing = f"   registers({addr})({mask[0]} downto {mask[1]}) <= {name}_i({mask[0]} downto {mask[1]});\n"

    access += """               if internal_master_out.we = '0' then
                  internal_master_in.ack <= '1';
                  internal_master_in.err <= '0';
               end if;
            end if;
"""

    formatters['Statuses Access'] += access
    formatters['Statuses Routing'] += routing

    if 'default' not in elem['Properties']:
        return

    if addr not in default_values:
        default_values[addr] = [(elem['Properties']['default'], mask)]


def generate_single_linear(name, elem, formatters, default_values):
    addr_lower = elem['Access']['Address']
    addr_upper = addr_lower + elem['Access']['Count'] - 1
    mask = elem['Access']['Mask']

    access = f"""
            {name} : if {addr_lower} <= internal_addr and internal_addr <= {addr_upper} then
               if internal_addr = {addr_upper} then
                  internal_master_in.dat({mask[0]} downto {mask[1]}) <= registers(internal_addr)({mask[0]} downto {mask[1]});
               else
                  internal_master_in.dat <= registers(internal_addr);
               end if;
"""
    routing = "TODO"

    access += """               if internal_master_out.we = '0' then
                  internal_master_in.ack <= '1';
                  internal_master_in.err <= '0';
               end if;
            end if;
"""

    formatters['Statuses Access'] += access
    formatters['Statuses Routing'] += routing


def generate_array(name, elem, formatters, default_values):
    formatters[
        'Entity Functional Ports'
    ] += f";\n      {name}_i : in t_slv_vector({elem['Count'] - 1} downto 0)({elem['Properties']['width'] - 1} downto 0)"

    strategy = elem['Access']['Strategy']
    if strategy == 'Single':
        generate_array_single(name, elem, formatters, default_values)
    if strategy == 'Multiple':
        generate_array_multiple(name, elem, formatters, default_values)


def generate_array_single(name, elem, formatters, default_values):
    base_addr = elem['Access']['Address']
    count = elem['Access']['Count']
    width = elem['Properties']['width']
    mask = elem['Access']['Mask']

    routing = f"""
   {name}_registers : for reg in 0 to {elem['Count'] - 1} generate
      registers({base_addr} + reg)({width - 1} downto 0) <= {name}_i(reg);
   end generate;
"""

    formatters['Statuses Routing'] += routing

    access = f"""
            {name} : if {base_addr} <= internal_addr and internal_addr <= {base_addr + count - 1} then
               internal_master_in.dat({width - 1} downto 0) <= registers(internal_addr)({width - 1} downto 0);
               if internal_master_out.we = '0' then
                  internal_master_in.ack <= '1';
                  internal_master_in.err <= '0';
               end if;
            end if;
"""

    formatters['Statuses Access'] += access

    if 'default' not in elem['Properties']:
        return

    default_values[(base_addr, base_addr + count - 1)] = [(elem['Properties']['default'], mask)]


def generate_array_multiple(name, elem, formatters):
    base_addr = elem['Access']['Address']
    count = elem['Count']
    width = elem['Properties']['width']
    items_per_access = elem['Access']['Items per Access']
    regs_count = elem['Access']['Count']

    if count % items_per_access == 0:
        routing = f"""
   {name}_registers : for reg in 0 to {regs_count - 1} generate
      {name}_items : for item in 0 to {items_per_access} - 1 generate
         registers({base_addr} + reg)({width} * (item + 1) - 1 downto {width} * item) <= {name}_i({items_per_access} * reg + item);
      end generate;
   end generate;
"""
    elif count < items_per_access:
        routing = f"""
   {name}_registers : for reg in 0 to {regs_count - 1} generate
      {name}_items : for item in 0 to {count - 1} generate
         registers({base_addr} + reg)({width} * (item + 1) - 1 downto {width} * item) <= {name}_i({items_per_access} * reg + item);
      end generate;
   end generate;
"""
    else:
        routing = f"""
   {name}_registers : for reg in 0 to {regs_count - 1} generate
      {name}_last_register : if reg = {regs_count - 1} generate
         {name}_tail_items : for item in 0 to {count % items_per_access - 1} generate
            registers({base_addr} + reg)({width} * (item + 1) - 1 downto {width} * item) <= {name}_i({items_per_access} * reg + item);
         end generate;
      else generate 
         {name}_head_items : for item in 0 to {items_per_access - 1} generate
            registers({base_addr} + reg)({width} * (item + 1) - 1 downto {width} * item) <= {name}_i({items_per_access} * reg + item);
         end generate;
      end generate;
   end generate;
"""

    formatters['Statuses Routing'] += routing
