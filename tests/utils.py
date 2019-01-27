"""Common tools for testing."""
# pylint: disable=too-many-arguments
from typing import Dict, List, Optional, Tuple
from uuid import uuid4, UUID

from gardnr import constants, drivers, metrics, models, reflection


TEST_TEMPERATURE = 42
TEST_METRIC = 'test-air-temperature'
TEST_POWER = 'test-power'
TEST_SENSOR = 'test-sensor'
TEST_EXPORTER = 'test-exporter'
TEST_SCHEDULE = 'test-schedule'
TEST_SCHEDULE_PROPERTIES = '* * * * *'  # every minute


UUID0 = UUID('00000000-0000-0000-0000-000000000000')
UUID1 = UUID('00000000-0000-0000-0000-000000000001')


class MockPower(drivers.Power):
    """A driver for testing, no hardware dependencies."""
    on_count = 0
    off_count = 0

    def on(self) -> None:
        MockPower.on_count += 1

    def off(self) -> None:
        MockPower.off_count += 1


class MockSensor(drivers.Sensor):
    """A driver for testing, no hardware dependencies."""

    def setup(self):
        self.sample_temperature = None  # type: int
        self.temperature_metric = None  # type: str

    def read(self) -> None:
        metrics.create_metric_log(self.temperature_metric,
                                  self.sample_temperature)


class MockExporter(drivers.Exporter):
    """An exporter for testing. Just logs how many times it logs"""
    call_count = 0

    def export(self, logs: List[models.MetricLog]) -> None:
        MockExporter.call_count += 1


def create_power_device(
        name: str = TEST_POWER,
        driver_type: type = MockPower,
        config: Optional[Dict] = None,
        disabled: bool = False
) -> models.Driver:
    fully_qualname = reflection.get_fully_qualname(driver_type)

    return models.Driver.create(
        name=name,
        type=constants.POWER,
        fully_qualname=fully_qualname,
        config=config,
        disabled=disabled
    )


def create_and_load_power_device(
        name: str = TEST_POWER,
        driver_type: type = MockPower,
        config: Optional[Dict] = None,
        disabled: bool = False
) -> drivers.Driver:
    power_device_model = create_power_device(name, driver_type,
                                             config, disabled)

    return reflection.load_driver(power_device_model)


def create_air_temperature_metric(
        metric_id: Optional[UUID] = None,
        metric_name: str = TEST_METRIC,
        metric_manual: bool = False,
        metric_disabled: bool = False
) -> models.Metric:

    if not metric_id:
        metric_id = uuid4()

    return models.Metric.create(id=metric_id,
                                name=metric_name,
                                topic=constants.AIR,
                                type=constants.T9E,
                                manual=metric_manual,
                                disabled=metric_disabled)


def create_air_temperature_sensor(
        metric_id: Optional[UUID] = None,
        metric_name: str = TEST_METRIC,
        metric_manual: bool = False,
        metric_disabled: bool = False,
        sample_temperature: float = TEST_TEMPERATURE,
        sensor_name: str = TEST_SENSOR,
        sensor_disabled: bool = False
) -> models.Driver:

    metric = create_air_temperature_metric(metric_id, metric_name,
                                           metric_manual, metric_disabled)

    fully_qualname = reflection.get_fully_qualname(MockSensor)
    config = dict(sample_temperature=sample_temperature,
                  temperature_metric=metric.name)
    return models.Driver.create(name=sensor_name,
                                type=constants.SENSOR,
                                fully_qualname=fully_qualname,
                                config=config,
                                disabled=sensor_disabled)


def create_and_load_air_temperature_sensor(
        metric_id: Optional[UUID] = None,
        metric_name: str = TEST_METRIC,
        metric_manual: bool = False,
        metric_disabled: bool = False,
        sample_temperature: float = TEST_TEMPERATURE,
        sensor_name: str = TEST_SENSOR,
        sensor_disabled: bool = False
) -> drivers.Driver:

    sensor_model = create_air_temperature_sensor(
        metric_id, metric_name, metric_manual, metric_disabled,
        sample_temperature, sensor_name, sensor_disabled
    )

    return reflection.load_driver(sensor_model)


def create_air_temperature_sensor_with_schedule(
        metric_id: Optional[UUID] = None,
        metric_name: str = TEST_METRIC,
        metric_manual: bool = False,
        metric_disabled: bool = False,
        sample_temperature: float = TEST_TEMPERATURE,
        sensor_name: str = TEST_SENSOR,
        sensor_disabled: bool = False,
        schedule_name: str = TEST_SCHEDULE,
        schedule_properties: str = TEST_SCHEDULE_PROPERTIES,
        schedule_disabled: bool = False
) -> Tuple[models.Driver, models.Schedule]:

    sensor = create_air_temperature_sensor(metric_id, metric_name,
                                           metric_manual, metric_disabled,
                                           sample_temperature, sensor_name,
                                           sensor_disabled)

    exploded_schedule_properties = schedule_properties.split(' ')
    assert len(exploded_schedule_properties) == 5

    schedule = models.Schedule.create(
        name=schedule_name,
        disabled=schedule_disabled,
        minute=exploded_schedule_properties[0],
        hour=exploded_schedule_properties[1],
        day_of_month=exploded_schedule_properties[2],
        month=exploded_schedule_properties[3],
        day_of_week=exploded_schedule_properties[4]
    )

    models.DriverSchedule.create(driver=sensor, schedule=schedule)

    return sensor, schedule


def create_exporter(
        name: str = TEST_EXPORTER,
        driver_type: type = MockExporter,
        config: Optional[Dict] = None,
        disabled: bool = False
) -> models.Driver:
    fully_qualname = reflection.get_fully_qualname(driver_type)

    return models.Driver.create(
        name=name,
        type=constants.EXPORTER,
        fully_qualname=fully_qualname,
        config=config,
        disabled=disabled
    )


def create_and_load_exporter(
        name: str = TEST_EXPORTER,
        driver_type: type = MockExporter,
        config: Optional[Dict] = None,
        disabled: bool = False
) -> drivers.Driver:
    exporter_model = create_exporter(name, driver_type, config, disabled)

    return reflection.load_driver(exporter_model)


def create_air_temperature_metric_trigger(
        metric_id: Optional[UUID] = None,
        metric_name: str = TEST_METRIC,
        metric_manual: bool = False,
        metric_disabled: bool = False,
        trigger_upper_bound: bool = True,
        trigger_disabled: bool = False,
        power_driver_name: str = TEST_POWER,
        power_driver_type: type = MockPower,
        power_driver_config: Optional[Dict] = None,
        power_driver_disabled: bool = False,
        power_on: bool = True
) -> Tuple[models.Metric, models.Trigger]:

    metric = create_air_temperature_metric(metric_id, metric_name,
                                           metric_manual, metric_disabled)

    power_driver = create_power_device(
        power_driver_name,
        power_driver_type,
        power_driver_config,
        power_driver_disabled
    )

    return models.Trigger.create(metric=metric,
                                 upper_bound=trigger_upper_bound,
                                 power_driver=power_driver,
                                 power_on=power_on,
                                 disabled=trigger_disabled)
