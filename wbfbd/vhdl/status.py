def generate(name, elem, formatters):
    if len(elem['Registers']) == 1:
        generate_single(name, elem, formatters)
    else:
        generate_array(name, elem, formatters)


def generate_single(name, elem, formatters):
    if name not in ['x_uuid_x', 'x_timestamp_x']:
        formatters[
            'Entity Functional Ports'
        ] += f";\n      {name}_i : in std_logic_vector({elem['Properties']['width'] - 1} downto 0)"

    indent = "            "
    regs = elem['Registers'][0]

    if len(regs) == 1:
        reg = regs[0]
        access = f"""
            {name} : if internal_addr = {reg[0]} then
               internal_master_in.dat({reg[1][0]} downto {reg[1][1]}) <= registers(internal_addr)({reg[1][0]} downto {reg[1][1]});
"""

        if name not in ['x_uuid_x', 'x_timestamp_x']:
            routing = f"   registers({reg[0]})({reg[1][0]} downto {reg[1][1]}) <= {name}_i({reg[1][0]} downto {reg[1][1]});\n"
        else:
            routing = ''
    else:
        access = f"""
            {name} : if {regs[0][0]} <= internal_addr and internal_addr <= {regs[-1][0]} then
               internal_master_in.dat({regs[0][1][0]} downto {regs[0][1][1]}) <= registers(internal_addr)({regs[0][1][0]} downto {regs[0][1][1]});
               if internal_addr = {regs[-1][0]} then
                  internal_master_in.dat <= registers(internal_addr)({regs[-1][1][0]} downto {regs[-1][1][1]});
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


def generate_array(name, elem, formatters):
    formatters[
        'Entity Functional Ports'
    ] += f";\n      {name}_i : in t_slv_vector({elem['Count'] - 1} downto 0)({elem['Properties']['width'] - 1} downto 0)"

    strategy = elem['Registers'].strategy
    if strategy == 'single':
        generate_array_single(name, elem, formatters)
    if strategy == 'multiple':
        generate_array_multiple(name, elem, formatters)


def generate_array_single(name, elem, formatters):
    base_addr = elem['Registers'].base_addr
    count = elem['Registers'].count
    width = elem['Properties']['width']

    routing = f"""
   {name}_registers : for reg in 0 to {elem['Count'] - 1} generate
      registers({base_addr} + reg)({width - 1} downto 0) <= {name}_i(reg);
   end generate;
"""

    formatters['Statuses Routing'] += routing

    access = f"""
            {name} : if {base_addr} <= internal_addr and internal_addr <= {base_addr} + {count} - 1 then
               internal_master_in.dat({width} - 1 downto 0) <= registers(internal_addr)({width} - 1 downto 0);
               if internal_master_out.we = '0' then
                  internal_master_in.ack <= '1';
                  internal_master_in.err <= '0';
               end if;
            end if;
"""

    formatters['Statuses Access'] += access


def generate_array_multiple(name, elem, formatters):
    base_addr = elem['Registers'].base_addr
    count = elem['Registers'].count
    width = elem['Properties']['width']
    items_per_access = elem['Registers'].items_per_access
    regs_count = elem['Registers'].registers_count

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
         {name}_tail_items : for reg in 0 to {count % items_per_access - 1} generate
            registers({base_addr} + reg)({width} * (item + 1) - 1 downto {width} * item) <= {name}_i({items_per_access} * reg + item);
         end generate;
      else generate 
         {name}_head_items : for reg in 0 to {items_per_access - 1} generate
            registers({base_addr} + reg)({width} * (item + 1) - 1 downto {width} * item) <= {name}_i({items_per_access} * reg + item);
         end generate;
      end generate;
   end generate;
"""

    formatters['Statuses Routing'] += routing
