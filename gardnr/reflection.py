import importlib
import sys
from typing import List, Optional

from gardnr import constants, drivers, models


def add_driver_path(path: str) -> None:
    """Adds path to PYTHONPATH"""
    sys.path.append(path)


def get_fully_qualname(cls: type) -> str:
    """module with qualified name"""
    return '{module}:{qualname}'.format(module=cls.__module__,
                                        qualname=cls.__qualname__)


def get_class_type(fully_qualname: str) -> type:
    """dynamically loads a class type"""
    module_name, class_name = fully_qualname.split(':')
    class_type = getattr(importlib.import_module(module_name),
                         class_name)

    if not class_type:
        raise NameError('Unable to load classfrom fully qualified '
                        'name {name}'.format(name=fully_qualname))

    return class_type


def load_driver(driver_model: models.Driver) -> drivers.Driver:
    """factory for configured driver objects"""

    class_type = get_class_type(driver_model.fully_qualname)

    return class_type(driver_model)


def load_active_drivers(
        driver_type: Optional[str] = None,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None
) -> List[drivers.Driver]:
    """Loads a list of Drivers by name that are not disabled"""

    driver_models = models.Driver.select().where(
        models.Driver.disabled == False
    )

    if driver_type:
        driver_models = driver_models.where(
            models.Driver.type == driver_type
        )

    if include:
        driver_models = driver_models.where(models.Driver.name.in_(include))
    elif exclude:
        driver_models = driver_models.where(models.Driver.name.not_in(exclude))

    return [load_driver(driver_model) for driver_model in driver_models]


def get_base_type(driver_class: type) -> str:
    if issubclass(driver_class, drivers.Sensor):
        return constants.SENSOR
    if issubclass(driver_class, drivers.Power):
        return constants.POWER
    elif issubclass(driver_class, drivers.Exporter):
        return constants.EXPORTER

    raise ValueError('Driver base type not found')
