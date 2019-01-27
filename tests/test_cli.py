# pylint: disable=protected-access

from unittest.mock import patch

import pytest

from gardnr import cli, models, tasks, reflection
from tests import utils


@pytest.mark.usefixtures('test_env')
def test_add_metric() -> None:

    _, args = cli.create_and_run_parser(['add', 'metric', 'air',
                                         'temperature', 'test-metric'])
    args.func(args)

    metrics = [metric for metric in models.Metric.select()]

    assert len(metrics) == 1


@pytest.mark.usefixtures('test_env')
def test_add_driver() -> None:

    _, args = cli.create_and_run_parser(['add', 'driver', 'test-driver',
                                         'tests.utils:MockSensor'])
    args.func(args)

    drivers = models.Driver.select()

    assert drivers.count() == 1


@pytest.mark.usefixtures('test_env')
def test_add_driver_with_config() -> None:

    driver_name = 'test-driver'

    _, args = cli.create_and_run_parser(['add', 'driver', driver_name,
                                         'tests.utils:MockSensor',
                                         '-c', 'foo=bar'])

    args.func(args)

    driver = models.Driver.get(models.Driver.name == driver_name)

    assert driver.config.get('foo') == 'bar'


@pytest.mark.usefixtures('test_env')
def test_add_schedule() -> None:

    schedule_name = 'test-schedule'

    _, args = cli.create_and_run_parser(
        ['add', 'schedule', schedule_name] +
        utils.TEST_SCHEDULE_PROPERTIES.split(' ')
    )

    # simulate console input
    with patch('builtins.input', side_effect='y'):
        args.func(args)

    schedule = models.Schedule.get(models.Schedule.name == schedule_name)

    assert schedule.crontab == utils.TEST_SCHEDULE_PROPERTIES


@pytest.mark.usefixtures('test_env')
def test_add_schedule_cancel() -> None:

    schedule_name = 'test-schedule'
    schedule_properties = ['*', '*', '*', '*', '*']

    _, args = cli.create_and_run_parser(['add', 'schedule', schedule_name] +
                                        schedule_properties)

    with patch('builtins.input', side_effect='n'):
        args.func(args)

    schedule = models.Schedule.get_or_none(
        models.Schedule.name == schedule_name)

    assert not schedule


@pytest.mark.usefixtures('test_env')
def test_add_schedule_force() -> None:

    schedule_name = 'test-schedule'
    schedule_properties = ['*', '*', '*', '*', '*']

    _, args = cli.create_and_run_parser(['add', 'schedule', schedule_name] +
                                        schedule_properties + ['-y'])

    args.func(args)

    schedule = models.Schedule.get(models.Schedule.name == schedule_name)

    assert schedule.crontab == ' '.join(schedule_properties)


@pytest.mark.usefixtures('test_env')
@pytest.mark.parametrize('bound, power', [('min', 'off'),
                                              ('min', 'on'),
                                              ('max', 'off'),
                                              ('max', 'on')])
def test_add_trigger(bound: str, power: str) -> None:

    upper_bound = cli._bound_to_bool(bound)

    metric = utils.create_air_temperature_metric()
    power_driver = utils.create_power_device()

    triggers1 = models.Trigger.select()
    assert triggers1.count() == 0

    _, args = cli.create_and_run_parser(['add', 'trigger', metric.name,
                                         bound, power_driver.name, power])

    args.func(args)

    triggers2 = models.Trigger.select()
    assert triggers2.count() == 1
    trigger = triggers2[0]
    assert trigger.metric.name == metric.name
    assert trigger.upper_bound == upper_bound
    assert trigger.power_driver.name == power_driver.name
    assert trigger.power_on == cli._power_to_bool(power)
    assert not trigger.disabled


@pytest.mark.usefixtures('test_env')
def test_remove_metric() -> None:
    """
    checks for the removal of metric's relationships
    """

    sensor = utils.create_and_load_air_temperature_sensor(
        metric_id=utils.UUID0)

    metric = models.Metric.get(models.Metric.id == utils.UUID0)

    exporter = utils.create_and_load_exporter()

    tasks.read([sensor])
    tasks.write([exporter])

    assert models.MetricLog.select().count() == 1
    assert models.ExportLog.select().count() == 1

    _, args = cli.create_and_run_parser(['remove', 'metric', metric.name])
    args.func(args)

    assert models.Metric.select().count() == 0
    assert models.MetricLog.select().count() == 0
    assert models.ExportLog.select().count() == 0

    #TODO: handle image metrics

@pytest.mark.usefixtures('test_env')
def test_remove_driver() -> None:

    utils.create_air_temperature_sensor()

    drivers1 = models.Driver.select()
    assert drivers1.count() == 1

    _, args = cli.create_and_run_parser(['remove', 'driver',
                                         utils.TEST_SENSOR])
    args.func(args)

    drivers2 = models.Driver.select()
    assert drivers2.count() == 0


@pytest.mark.usefixtures('test_env')
def test_remove_exporter() -> None:

    sensor = utils.create_and_load_air_temperature_sensor()

    exporter = utils.create_and_load_exporter()

    tasks.read([sensor])
    tasks.write([exporter])

    assert models.ExportLog.select().count() == 1

    _, args = cli.create_and_run_parser(
        ['remove', 'driver', exporter.model.name])
    args.func(args)

    assert models.Driver.select().\
        where(models.Driver.id == exporter.model.id).count() == 0
    assert models.ExportLog.select().count() == 0


@pytest.mark.usefixtures('test_env')
def test_remove_schedule() -> None:

    utils.create_air_temperature_sensor_with_schedule()

    drivers1 = models.Driver.select()
    assert drivers1.count() == 1
    schedules1 = models.Schedule.select()
    assert schedules1.count() == 1
    driver_schedules1 = models.DriverSchedule.select()
    assert driver_schedules1.count() == 1

    _, args = cli.create_and_run_parser(['remove', 'schedule',
                                         utils.TEST_SCHEDULE])
    args.func(args)

    drivers2 = models.Driver.select()
    assert drivers2.count() == 1
    schedules2 = models.Schedule.select()
    assert schedules2.count() == 0
    driver_schedules2 = models.DriverSchedule.select()
    assert driver_schedules2.count() == 0


@pytest.mark.usefixtures('test_env')
@pytest.mark.parametrize('bound, power', [('min', 'off'),
                                              ('min', 'on'),
                                              ('max', 'off'),
                                              ('max', 'on')])
def test_remove_trigger(bound: str, power: str) -> None:

    upper_bound = cli._bound_to_bool(bound)
    powered_on = cli._power_to_bool(power)

    trigger = utils.create_air_temperature_metric_trigger(
        trigger_upper_bound=upper_bound,
        power_on=powered_on
    )

    triggers1 = models.Trigger.select()
    assert triggers1.count() == 1

    _, args = cli.create_and_run_parser(['remove', 'trigger',
                                         trigger.metric.name, bound,
                                         trigger.power_driver.name, power])

    args.func(args)

    triggers2 = models.Trigger.select()
    assert triggers2.count() == 0


@pytest.mark.usefixtures('test_env')
def test_disable_metric() -> None:

    metric = utils.create_air_temperature_metric()

    metrics1 = models.Metric.select()
    assert metrics1.count() == 1

    _, args = cli.create_and_run_parser(['disable', 'metric', metric.name])
    args.func(args)

    metric2 = models.Metric.get(models.Metric.name == metric.name)
    assert metric2.disabled

    _, args = cli.create_and_run_parser(['enable', 'metric', metric.name])
    args.func(args)

    metric3 = models.Metric.get(models.Metric.name == metric.name)
    assert not metric3.disabled


@pytest.mark.usefixtures('test_env')
def test_disable_driver() -> None:

    sensor = utils.create_air_temperature_sensor()

    assert not sensor.disabled

    _, args = cli.create_and_run_parser(['disable', 'driver', sensor.name])
    args.func(args)

    sensor2 = models.Driver.get(models.Driver.name == sensor.name)
    assert sensor2.disabled

    _, args = cli.create_and_run_parser(['enable', 'driver', sensor.name])
    args.func(args)

    sensor3 = models.Driver.get(models.Driver.name == sensor.name)
    assert not sensor3.disabled


@pytest.mark.usefixtures('test_env')
def test_disable_schedule() -> None:

    _, schedule = utils.create_air_temperature_sensor_with_schedule()

    assert not schedule.disabled

    _, args = cli.create_and_run_parser(['disable', 'schedule', schedule.name])
    args.func(args)

    schedule2 = models.Schedule.get(models.Schedule.name == schedule.name)
    assert schedule2.disabled

    _, args = cli.create_and_run_parser(['enable', 'schedule', schedule.name])
    args.func(args)

    schedule3 = models.Schedule.get(models.Schedule.name == schedule.name)
    assert not schedule3.disabled


@pytest.mark.usefixtures('test_env')
@pytest.mark.parametrize('bound', ['min', 'max'])
def test_disable_trigger(bound: str) -> None:

    upper_bound = cli._bound_to_bool(bound)

    trigger = utils.create_air_temperature_metric_trigger(
        trigger_upper_bound=upper_bound)

    assert not trigger.disabled

    _, args = cli.create_and_run_parser(['disable', 'trigger',
                                         trigger.metric.name, bound])
    args.func(args)

    trigger1 = models.Trigger.get(models.Trigger.metric == trigger.metric,
                                  models.Trigger.upper_bound == upper_bound)
    assert trigger1.disabled

    _, args = cli.create_and_run_parser(['enable', 'trigger',
                                         trigger.metric.name, bound])
    args.func(args)

    trigger2 = models.Trigger.get(models.Trigger.metric == trigger.metric,
                                  models.Trigger.upper_bound == upper_bound)
    assert not trigger2.disabled


@pytest.mark.usefixtures('test_env')
def test_schedule_driver() -> None:
    sensor, schedule = utils.create_air_temperature_sensor_with_schedule()

    driver_schedules = models.DriverSchedule.select()
    assert driver_schedules.count() == 1

    _, args = cli.create_and_run_parser(['schedule', 'remove', sensor.name,
                                         schedule.name])
    args.func(args)

    driver_schedules2 = models.DriverSchedule.select()
    assert driver_schedules2.count() == 0

    _, args = cli.create_and_run_parser(['schedule', 'add', sensor.name,
                                         schedule.name])
    args.func(args)

    driver_schedules3 = models.DriverSchedule.select()
    assert driver_schedules3.count() == 1


@pytest.mark.usefixtures('test_env')
def test_schedule_driver_power() -> None:
    power_device = utils.create_power_device()

    schedule_on = models.Schedule.create(
        name='test-schedule-on',
        minute='0',
        hour='6',
        day_of_month='*',
        month='*',
        day_of_week='*'
    )

    schedule_off = models.Schedule.create(
        name='test-schedule-off',
        minute='0',
        hour='18',
        day_of_month='*',
        month='*',
        day_of_week='*'
    )

    driver_schedules = models.DriverSchedule.select()
    assert driver_schedules.count() == 0

    # missing power argument, driver schedule shouldnt be added
    _, args = cli.create_and_run_parser(['schedule', 'add', power_device.name,
                                         schedule_on.name])
    args.func(args)

    driver_schedules2 = models.DriverSchedule.select()
    assert driver_schedules2.count() == 0

    # invalid argument for power, driver schedule shouldnt be added
    """
    with pytest.raises(argparse.ArgumentError):
        _, args = cli.create_and_run_parser(['schedule', 'add',
                                             power_device.name,
                                             schedule_on.name, 'invalid'])
    args.func(args)

    driver_schedules3 = models.DriverSchedule.select()
    assert driver_schedules3.count() == 0
    """

    _, args = cli.create_and_run_parser(['schedule', 'add', power_device.name,
                                         schedule_on.name, 'on'])
    args.func(args)
    driver_schedules4 = models.DriverSchedule.select()
    assert driver_schedules4.count() == 1
    assert driver_schedules4[0].power_on

    _, args = cli.create_and_run_parser(['schedule', 'add', power_device.name,
                                         schedule_off.name, 'off'])
    args.func(args)
    driver_schedules5 = models.DriverSchedule.select()
    assert driver_schedules5.count() == 2

    driver_schedules6 = driver_schedules5.join(models.Schedule)\
        .where(models.Schedule.name == schedule_off.name)
    assert driver_schedules6.count() == 1
    assert not driver_schedules6[0].power_on


@pytest.mark.usefixtures('test_env')
def test_manual() -> None:

    # should return that metric does not exist
    _, args = cli.create_and_run_parser(['manual', 'off', utils.TEST_METRIC])
    args.func(args)
    metric = utils.create_air_temperature_metric()
    assert not metric.manual

    # update metric model from database after running cli function
    _, args = cli.create_and_run_parser(['manual', 'off', utils.TEST_METRIC])
    args.func(args)
    metric = models.Metric.get(models.Metric.name == metric.name)
    assert not metric.manual

    _, args = cli.create_and_run_parser(['manual', 'on', utils.TEST_METRIC])
    args.func(args)
    metric = models.Metric.get(models.Metric.name == metric.name)
    assert metric.manual

    _, args = cli.create_and_run_parser(['manual', 'on', utils.TEST_METRIC])
    args.func(args)
    metric = models.Metric.get(models.Metric.name == metric.name)
    assert metric.manual


@pytest.mark.usefixtures('test_env')
def test_read_include() -> None:
    utils.create_air_temperature_sensor(sensor_name='sensor1')
    sensor2 = utils.create_and_load_air_temperature_sensor(
        metric_name='metric2',
        sensor_name='sensor2')

    _, args = cli.create_and_run_parser(
        ['read', '--include', sensor2.model.name])

    with patch('gardnr.tasks.read') as mock_write:
        args.func(args)

    call_args, _ = mock_write.call_args
    called_sensors = call_args[0]

    assert len(called_sensors) == 1
    assert called_sensors[0].model.name == sensor2.model.name


@pytest.mark.usefixtures('test_env')
def test_read_exclude() -> None:
    sensor1 = utils.create_and_load_air_temperature_sensor(
        sensor_name='sensor1')
    sensor2 = utils.create_and_load_air_temperature_sensor(
        metric_name='metric2',
        sensor_name='sensor2')

    _, args = cli.create_and_run_parser(
        ['read', '--exclude', sensor2.model.name])

    with patch('gardnr.tasks.read') as mock_write:
        args.func(args)

    call_args, _ = mock_write.call_args
    called_sensors = call_args[0]

    assert len(called_sensors) == 1
    assert called_sensors[0].model.name == sensor1.model.name


@pytest.mark.usefixtures('test_env')
def test_write_include() -> None:
    utils.create_exporter('exporter1')
    exporter2 = utils.create_and_load_exporter('exporter2')

    _, args = cli.create_and_run_parser(
        ['write', '--include', exporter2.model.name])

    with patch('gardnr.tasks.write') as mock_write:
        args.func(args)

    call_args, _ = mock_write.call_args
    called_exporters = call_args[0]

    assert len(called_exporters) == 1
    assert called_exporters[0].model.name == exporter2.model.name


@pytest.mark.usefixtures('test_env')
def test_power_on() -> None:
    power_device = utils.create_and_load_power_device()

    _, args = cli.create_and_run_parser(
        ['power', 'on', power_device.model.name])

    with patch('gardnr.tasks.power_on') as mock_power_on:
        args.func(args)

    call_args, _ = mock_power_on.call_args
    called_power_devices = call_args[0]

    assert len(called_power_devices) == 1
    assert called_power_devices[0].model.name == power_device.model.name


@pytest.mark.usefixtures('test_env')
def test_power_off() -> None:
    power_device = utils.create_and_load_power_device()

    _, args = cli.create_and_run_parser(
        ['power', 'off', power_device.model.name])

    with patch('gardnr.tasks.power_off') as mock_power_off:
        args.func(args)

    call_args, _ = mock_power_off.call_args
    called_power_devices = call_args[0]

    assert len(called_power_devices) == 1
    assert called_power_devices[0].model.name == power_device.model.name
