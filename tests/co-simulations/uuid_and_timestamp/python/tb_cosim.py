import logging as log
log.basicConfig(
    level=log.DEBUG,
    format="%(module)s:%(levelname)s:%(message)s",
    datefmt="%H:%M:%S",
)

from cosim_interface import CosimInterface

WRITE_FIFO_PATH = "/tmp/PyWbFBD/uuid_and_timestamp_vhdl"
READ_FIFO_PATH  = "/tmp/PyWbFBD/uuid_and_timestamp_python"

CLOCK_PERIOD_40 = 25


def delay_function():
    return CLOCK_PERIOD_40 * random.randrange(10,40)


try:
    log.info("Starting cosimulation")

    cosim_interface = CosimInterface(WRITE_FIFO_PATH, READ_FIFO_PATH, delay_function, True)

    #agwb_top = agwb.top(cosim_interface, 0)

    cosim_interface.wait(10 * CLOCK_PERIOD_40)
    log.info("Ending cosimulation")
    cosim_interface.end(0)

except Exception as E:
    cosim_interface.end(1)
    log.exception(E)
