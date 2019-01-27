from typing import List

from gardnr import drivers, logger, metrics


def power_on(power_devices: List[drivers.Power]) -> None:
    for power_device in power_devices:
        logger.info('Powered on {}'.format(power_device.model.name))
        power_device.on()


def power_off(power_devices: List[drivers.Power]) -> None:
    for power_device in power_devices:
        logger.info('Powering off {}'.format(power_device.model.name))
        power_device.off()
