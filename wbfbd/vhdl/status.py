def generate(name, elem, formatters):
    if len(elem['Registers']) == 1:
        generate_single(name, elem, formatters)
    else:
        generate_array(name, elem, formatters)


def generate_single(name, elem, formatters):
    if name not in ['x_uuid_x', 'x_timestamp_x']:
        formatters[
            'Entity Functional Ports'
        ] += f";\n      {name}_i : in std_logic_vector({elem['Properties']['width']} - 1 downto 0)"

    indent = "            "
    access = ''
    routing = ''
    regs = elem['Registers'][0]

    if len(regs) == 1:
        access += indent + f"{name} : if internal_addr = {regs[0][0]} then\n"
        access += (
            indent
            + f"   internal_master_in.dat <= registers(internal_addr)({regs[0][1][0]} downto {regs[0][1][1]});\n"
        )

        if name not in ['x_uuid_x', 'x_timestamp_x']:
            routing += f"   registers({regs[0][0]})({regs[0][1][0]} downto {regs[0][1][1]}) <= {name}_i({regs[0][1][0]} downto {regs[0][1][1]});\n"
    else:
        access += (
            indent
            + f"{name} : if {regs[0][0]} <= internal_addr and internal_addr <= {regs[-1][0]} then\n"
        )
        access += (
            indent
            + f"   internal_master_in.dat <= registers(internal_addr)({regs[0][1][0]} downto {regs[0][1][1]});\n"
        )
        access += indent + f"   if internal_addr = {regs[-1][0]} then\n"
        access += (
            indent
            + f"      internal_master_in.dat <= registers(internal_addr)({regs[-1][1][0]} downto {regs[-1][1][1]});\n"
        )
        access += indent + "   end if;\n"

    access += indent + "   if internal_master_out.we = '0' then\n"
    access += indent + "      internal_master_in.ack <= '1';\n"
    access += indent + "      internal_master_in.err <= '0';\n"
    access += indent + "   end if;\n"

    formatters['Statuses Access'] += access + indent + "end if;\n"
    formatters['Statuses Routing'] += routing


def generate_array(name, elem, formatters):
    pass
