#!/usr/bin/env python
"""
Runs the scheduler and workers of scheduled tasks for drivers
"""
from datetime import timedelta
from typing import List, TextIO, Tuple

from apscheduler.schedulers.blocking import BlockingScheduler

from gardnr import constants, drivers, grow, logger, models, reflection, tasks, settings


trigger_bounds = []  # List[TriggerBound]
active_trigger_bounds = []  # List[TriggerBound]


def main() -> None:

    logger.setup()

    logger.info('Starting automata')

    models.initialize_db()

    reflection.add_driver_path(settings.DRIVER_PATH)

    scheduler = BlockingScheduler()

    schedules = models.Schedule.select()\
        .where(models.Schedule.disabled == False)
    for schedule in schedules:

        driver_names = _build_driver_dict(schedule)

        scheduler.add_job(
            driver_worker,
            'cron',
            [*driver_names],
            minute=schedule.minute,
            hour=schedule.hour,
            day=schedule.day_of_month,
            month=schedule.month,
            day_of_week=schedule.day_of_week,
        )

    tracked_grow = grow.get_tracked_grow()

    if tracked_grow:
        with open(settings.GROW_RECIPE) as recipe:
            _build_trigger_bounds(tracked_grow, recipe)

        scheduler.add_job(
            bound_checker,
            'interval',
            minutes=settings.BOUND_CHECK_FREQUENCY
        )

    scheduler.start()


def _build_driver_dict(
        schedule: models.Schedule
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    Helper function to build a dict with the drivers names categorized
    into what type and action they require
    """

    power_on_names = []
    power_off_names = []
    sensor_names = []
    exporter_names = []

    for driver_schedule in schedule.driver_schedules:
        driver = driver_schedule.driver

        if driver.type == constants.POWER:
            if driver_schedule.power_on:
                power_on_names.append(driver.name)
            else:
                power_off_names.append(driver.name)
        elif driver.type == constants.SENSOR:
            sensor_names.append(driver.name)
        elif driver.type == constants.EXPORTER:
            exporter_names.append(driver.name)

    return power_on_names, power_off_names, sensor_names, exporter_names


def driver_worker(
        power_on_names: List[str],
        power_off_names: List[str],
        sensor_names: List[str],
        exporter_names: List[str]
) -> None:

    if power_on_names:
        power_on_drivers = reflection.load_active_drivers(
            constants.POWER,
            power_on_names
        )
        tasks.power_on(power_on_drivers)

    if power_off_names:
        power_off_drivers = reflection.load_active_drivers(
            constants.POWER,
            power_off_names
        )
        tasks.power_off(power_off_drivers)

    if sensor_names:
        sensors = reflection.load_active_drivers(
            constants.SENSOR,
            sensor_names
        )
        tasks.read(sensors)

    if exporter_names:
        exporters = reflection.load_active_drivers(
            constants.EXPORTER,
            exporter_names
        )
        tasks.write(exporters)


class TriggerBound:
    """
    A class to dynamically link configured triggers with a grow recipe bound
    """
    def __init__(
            self,
            trigger: models.Trigger,
            bound: float,
            power_driver: drivers.Power
    ) -> None:
        self.trigger = trigger
        self.bound = bound
        self.power_driver = power_driver


def _build_trigger_bounds(
        tracked_grow: models.Grow,
        recipe: TextIO
) -> None:

    active_triggers = models.Trigger.select().where(
        models.Trigger.disabled == False)

    for trigger in active_triggers:
        metric_bound = grow.get_metric_bound(
            recipe, tracked_grow, trigger.metric.topic, trigger.metric.type)

        if metric_bound:
            power_driver = reflection.load_driver(trigger.power_driver)

            if metric_bound.min is not None and not trigger.upper_bound:
                trigger_bounds.append(TriggerBound(
                    trigger, metric_bound.min, power_driver))
            elif metric_bound.max is not None and trigger.upper_bound:
                trigger_bounds.append(TriggerBound(
                    trigger, metric_bound.max, power_driver))


def bound_checker() -> None:

    def _is_out_of_bound(tb: TriggerBound, log: models.MetricLog) -> bool:

        if tb.trigger.upper_bound and\
           log.value > tb.bound:
            return True

        elif not tb.trigger.upper_bound and\
                log.value < tb.bound:
            return True

        return False

    # check to reverse the trigger action
    for tb in active_trigger_bounds:
        # check since the last run
        latest_log = tb.trigger.metric.get_latest_log(
            timedelta(minutes=settings.BOUND_CHECK_FREQUENCY))

        if latest_log and not _is_out_of_bound(tb, latest_log):
            log_str = ('Turning {{on_off}} {power_driver_name} to reverse '
                       'the action for {metric_name} being too '
                       '{low_high}').format(
                           power_driver_name=tb.trigger.power_driver.name,
                           metric_name=tb.trigger.metric.name,
                           low_high=('high' if tb.trigger.upper_bound
                                     else 'low'))

            reflection.load_driver(tb.trigger.power_driver)

            if tb.trigger.power_on:
                logger.info(log_str.format(on_off='off'))
                tb.power_driver.off()
            else:
                logger.info(log_str.format(on_off='on'))
                tb.power_driver.on()

            active_trigger_bounds.remove(tb)

    for tb in trigger_bounds:
        latest_log = tb.trigger.metric.get_latest_log(
            timedelta(minutes=settings.BOUND_CHECK_FREQUENCY))

        if latest_log and _is_out_of_bound(tb, latest_log):
            log_str = ('Turning {{on_off}} {power_driver_name} because '
                       '{metric_name} is too {low_high}').format(
                           power_driver_name=tb.trigger.power_driver.name,
                           metric_name=tb.trigger.metric.name,
                           low_high=('high' if tb.trigger.upper_bound
                                     else 'low'))

            if tb.trigger.power_on:
                logger.info(log_str.format(on_off='on'))
                tb.power_driver.on()
            else:
                logger.info(log_str.format(on_off='off'))
                tb.power_driver.off()

            active_trigger_bounds.append(tb)


if __name__ == '__main__':
    main()
