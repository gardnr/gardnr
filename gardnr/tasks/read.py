from typing import List

from gardnr import drivers


def read(sensors: List[drivers.Sensor]) -> None:
    """
    Iterate over every sensor and read from it and create logs and store
    them in database.
    """
    for sensor in sensors:
        # TODO: should be a better way to do this https://goo.gl/xrJdpv
        sensor.read()  # type: ignore
