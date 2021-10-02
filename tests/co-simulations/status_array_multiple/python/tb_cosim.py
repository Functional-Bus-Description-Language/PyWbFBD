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

    log.info("Testing count % iterm per access = 0 scenerio.")

    values = main.status_array0.read()
    assert len(values) == 9
    for i, v in enumerate(values):
        assert v == i

    idx = [2, 7]
    values = main.status_array0.read(idx)
    assert values[0] == 2
    assert values[1] == 7

    value = main.status_array0.read(5)
    assert value == 5

    log.info("Testing count < items per access scenario.")

    values = main.status_array1.read()
    assert len(values) == 4
    for i, v in enumerate(values):
        assert v == i

    idx = [0, 3]
    values = main.status_array1.read(idx)
    assert values[0] == 0
    assert values[1] == 3

    value = main.status_array1.read(2)
    assert value == 2

    log.info("Testing scenerio when the number of items in the last register is different.")

    values = main.status_array2.read()
    assert len(values) == 6
    for i, v in enumerate(values):
        assert v == i

    idx = [1, 5]
    values = main.status_array2.read(idx)
    assert values[0] == 1
    assert values[1] == 5

    value = main.status_array2.read(0)
    assert value == 0
    cosim_interface.wait(10 * CLOCK_PERIOD_40)

    log.info("Ending cosimulation")
    cosim_interface.end(0)

except Exception as E:
    cosim_interface.end(1)
    log.exception(E)
