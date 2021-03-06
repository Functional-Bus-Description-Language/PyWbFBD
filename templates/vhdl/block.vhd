-- This file has been automatically generated by the wbfbd tool.
-- Do not edit it manually, unless you really know what you do.
-- https://github.com/Functional-Bus-Description-Language/PyWbFBD

library ieee;
   use ieee.std_logic_1164.all;

package {Entity Name}_pkg is

{Constants}
end package;


library ieee;
   use ieee.std_logic_1164.all;
   use ieee.numeric_std.all;

library general_cores;
   use general_cores.wishbone_pkg.all;

library work;
   use work.wbfbd.all;

use work.{Entity Name}_pkg.all;


entity {Entity Name} is
   generic (
      G_REGISTERED : boolean := true
   );
   port (
      clk_i : in std_logic;
      rst_i : in std_logic;
      slave_i : in  t_wishbone_slave_in_array ({Number of Masters} - 1 downto 0);
      slave_o : out t_wishbone_slave_out_array({Number of Masters} - 1 downto 0){Entity Subblock Ports}{Entity Functional Ports}
   );
end entity;


architecture rtl of {Entity Name} is

   constant C_ADDRESSES : t_wishbone_address_array({Number of Subblocks} downto 0) := ({Address Values});
   constant C_MASKS     : t_wishbone_address_array({Number of Subblocks} downto 0) := ({Mask Values});

   constant C_REGISTER_UNINITIALIZED_VALUE : std_logic_vector({Bus Width} - 1 downto 0) := (others => 'U');
   subtype t_register_vector is t_slv_vector({Number of Registers} - 1 downto 0)({Bus Width} - 1 downto 0);
   signal registers : t_register_vector := ({Default Values}others => C_REGISTER_UNINITIALIZED_VALUE);

   signal internal_master_out : t_wishbone_master_out;
   signal internal_master_in  : t_wishbone_master_in;

{Signal Declarations}
begin

   crossbar: entity general_cores.xwb_crossbar
   generic map (
      G_NUM_MASTERS => {Number of Masters},
      G_NUM_SLAVES  => {Number of Subblocks} + 1,
      G_REGISTERED  => G_REGISTERED,
      G_ADDRESS     => C_ADDRESSES,
      G_MASK        => C_MASKS
   )
   port map (
      clk_sys_i   => clk_i,
      rst_n_i     => not rst_i,
      slave_i     => slave_i,
      slave_o     => slave_o,
      master_i(0) => internal_master_in,
      master_o(0) => internal_master_out{Crossbar Subblock Ports}
   );


   {Statuses Routing}

   register_access : process (clk_i) is
      variable internal_addr : natural range 0 to {Number of Registers} - 1;
   begin
      if rising_edge(clk_i) then
         -- Normal operation.
         internal_master_in.rty <= '0';
         internal_master_in.ack <= '0';
         internal_master_in.err <= '0';

         transfer : if
            internal_master_out.cyc = '1'
            and internal_master_out.stb = '1'
            and internal_master_in.err = '0'
            and internal_master_in.rty = '0'
            and internal_master_in.ack = '0'
         then
            internal_addr := to_integer(unsigned(internal_master_out.adr({Number of Internal Address Bits} - 1 downto 0)));

            -- First assume there is some kind of error.
            -- For example internal address is invalid or there is a try to write status.
            internal_master_in.err <= '1';
            -- '0' for security reasons, '-' can lead to the information leak.
            internal_master_in.dat <= (others => '0');
            internal_master_in.ack <= '0';

            {Statuses Access}
         end if transfer;

         if rst_i = '1' then
            internal_master_in <= C_DUMMY_WB_MASTER_IN;
         end if;
      end if;
   end process;

end architecture;
