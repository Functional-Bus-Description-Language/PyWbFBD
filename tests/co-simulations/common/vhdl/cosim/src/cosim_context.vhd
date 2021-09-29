context cosim_context is
   library ieee;
      use ieee.std_logic_1164.all;
      use ieee.numeric_std.all;

   library wbfbd;
      use wbfbd.wbfbd.all;
      use wbfbd.main_pkg.all;

   library general_cores;
      use general_cores.wishbone_pkg.all;

   library uvvm_util;
      context uvvm_util.uvvm_util_context;

   library bitvis_vip_wishbone;
      use bitvis_vip_wishbone.wishbone_bfm_pkg.all;
end context;
