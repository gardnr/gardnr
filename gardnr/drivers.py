"""
Abstract driver classes as well as common purpose mixins, all custom
drivers must inhereit at least one of these. Drivers hold the code
that interacts with the connected hardware.
"""
from abc import ABCMeta, abstractmethod
from typing import List

from gardnr import constants, logger, models


class Driver(metaclass=ABCMeta):
    """
    Base driver class. Containts features to have "user defined configuration"
    which can be loaded from a JSON string
    """

    def __init__(self, model: models.Driver) -> None:
        """holds user defined configs for drivers and transmitters"""
        self.model = model

        self.setup()

        if self.model.config is not None:
            for key, value in self.model.config.items():
                if hasattr(self, key):
                    logger.warning('{name} is overriding attribute {key} for '
                                   '{qualname}.'.format(
                                       name=self.model.name,
                                       key=key,
                                       qualname=type(self).__qualname__))
                setattr(self, key, value)

    def setup(self) -> None:
        """Do not override __init__, override setup instead."""
        pass

    @property
    @staticmethod
    @abstractmethod
    def type() -> str:
        raise NotImplementedError()


class Power(Driver, metaclass=ABCMeta):
    """supplies power to electrical equiptment"""

    @property
    @staticmethod
    def type() -> str:
        return constants.POWER

    def on(self) -> None:
        """enables power through to connected electrical equiptment"""
        raise NotImplementedError()

    def off(self) -> None:
        """disables power through to connected electrical equiptment"""
        raise NotImplementedError()


class Sensor(Driver, metaclass=ABCMeta):
    """Base sensor specific functions"""

    @property
    @staticmethod
    def type() -> str:
        return constants.SENSOR

    def read(self) -> None:
        """get the readings of the sensor"""
        raise NotImplementedError()


class Exporter(Driver, metaclass=ABCMeta):
    """Base exporter class, all exporter must inherit this."""

    whitelist = None
    blacklist = None

    @property
    @staticmethod
    def type() -> str:
        return constants.EXPORTER

    def export(self, logs: List[models.MetricLog]) -> None:
        """send logs to destination"""
        raise NotImplementedError()
