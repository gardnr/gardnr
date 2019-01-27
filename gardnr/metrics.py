import os
from typing import Any
from uuid import uuid4

from gardnr import constants, models, settings


def create_metric_log(metric_name: str, value: Any) -> models.MetricLog:
    """sets up common metric log fields"""

    metric = models.Metric.get(models.Metric.name == metric_name)

    return models.MetricLog.create(id=uuid4(), metric=metric, value=value)


def create_file_log(metric_name: str,
                    blob: bytes,
                    extension: str) -> models.MetricLog:
    """
    Creates a special metric log for blob (bytes) type
    metrics, i.e. images and videos. The value of the metric
    is the path of the stored file. The blob is then written
    to disk.

    NOTE: extension should be in the format '.jpg' which includes
    the beginning .
    """

    metric = models.Metric.get(models.Metric.name == metric_name)

    uuid = uuid4()

    uploaded_file_name = '{uuid}{extension}'.format(
        uuid=str(uuid).replace('-', ''),
        extension=extension
    )

    full_path = os.path.join(settings.UPLOAD_PATH, uploaded_file_name)

    open(full_path, 'wb').write(blob)

    return models.MetricLog.create(id=uuid,
                                   metric=metric,
                                   value=full_path)


class MetricBase:

    @staticmethod
    def standardize(value: float) -> Any:
        """
        Check settings to convert localized metric value to standardized one
        """
        return value

    @staticmethod
    def validate(value: Any) -> bool:
        del value
        return True


class TemperatureMetric(MetricBase):

    @staticmethod
    def fahrenheit_to_celsius(fahrenheit_temperature: float) -> float:
        return (fahrenheit_temperature - 32) * 5/9

    @staticmethod
    def standardize(value: float) -> float:
        """Creates temperature log"""

        if settings.TEMPERATURE_UNIT == constants.FAHRENHEIT:
            value = TemperatureMetric.fahrenheit_to_celsius(value)

        return value


class HumidityMetric(MetricBase):

    @staticmethod
    def validate(value: float) -> bool:
        return value >= 0 and value <= 1


def standardize_metric(metric_type: str, value: float) -> float:
    """Convert metric value from localized version to standardized one"""

    if metric_type == constants.T9E:
        value = TemperatureMetric.standardize(value)

    return value
