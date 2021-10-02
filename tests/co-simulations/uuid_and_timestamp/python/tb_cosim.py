import sys

import logging as log
log.basicConfig(
    level=log.DEBUG,
    format="%(module)s:%(levelname)s:%(message)s",
    datefmt="%H:%M:%S",
)
import random

from cosim_interface import CosimInterface
import wbfbd

WRITE_FIFO_PATH = sys.argv[1]
READ_FIFO_PATH  = sys.argv[2]

CLOCK_PERIOD_40 = 25


def delay_function():
    return CLOCK_PERIOD_40 * random.randrange(10, 40)


try:
    log.info("Starting cosimulation")

    cosim_interface = CosimInterface(WRITE_FIFO_PATH, READ_FIFO_PATH, delay_function, True)

    main = wbfbd.class_main(cosim_interface)

    print(f"UUID: {main.x_uuid_x.read()}")
    print(f"Timestamp: {main.x_timestamp_x.read()}")

    cosim_interface.wait(10 * CLOCK_PERIOD_40)
    log.info("Ending cosimulation")
    cosim_interface.end(0)

except Exception as E:
    cosim_interface.end(1)
    log.exception(E)
