library work;
   context work.cosim_context;
   use work.cosim.all;


entity tb_cosim is
end entity;


architecture test of tb_cosim is

   constant C_READ_FIFO_PATH  : string := "/tmp/PyWbFBD/status_array_single_vhdl";
   constant C_WRITE_FIFO_PATH : string := "/tmp/PyWbFBD/status_array_single_python";

   signal clk : std_logic := '0';

   signal status_array : t_slv_vector(8 downto 0)(16 downto 0) := (
      0 => "00000000000000000",
      1 => "00000000000000001",
      2 => "00000000000000010",
      3 => "00000000000000011",
      4 => "00000000000000100",
      5 => "00000000000000101",
      6 => "00000000000000110",
      7 => "00000000000000111",
      8 => "00000000000001000"
   );

   -- Wishbone interfaces.
   signal uvvm_wb_if : t_wishbone_if (
      dat_o(31 downto 0),
      dat_i(31 downto 0),
      adr_o(31 downto 0)
   ) := init_wishbone_if_signals(32, 32);

   signal wb_ms: t_wishbone_master_out;
   signal wb_sm: t_wishbone_slave_out;

begin

   clk <= not clk after C_CLK_PERIOD / 2;


   wb_ms.cyc <= uvvm_wb_if.cyc_o;
   wb_ms.stb <= uvvm_wb_if.stb_o;
   wb_ms.adr <= uvvm_wb_if.adr_o;
   wb_ms.sel <= (others => '0');
   wb_ms.we  <= uvvm_wb_if.we_o;
   wb_ms.dat <= uvvm_wb_if.dat_o;

   uvvm_wb_if.dat_i <= wb_sm.dat;
   uvvm_wb_if.ack_i <= wb_sm.ack;

   cosim_interface(C_READ_FIFO_PATH, C_WRITE_FIFO_PATH, clk, uvvm_wb_if, C_WB_BFM_CONFIG);


   wbfbd_main : entity wbfbd.main
   port map (
      clk_i => clk,
      rst_i => '0',
      slave_i(0) => wb_ms,
      slave_o(0) => wb_sm,
      status_array_i => status_array
   );

end architecture;
