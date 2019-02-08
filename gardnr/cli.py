#!/usr/bin/env python
"""
Contains entry point to the program and command line parsing
"""

import argparse
import sys
import uuid
import os
import shutil
from datetime import datetime
from typing import List, Optional, Tuple

from gardnr import (constants, grow, logger, models,
                    reflection, settings, tasks)

LOGO = (r"""
 #####      #     ######   ######   #     #  ######
#     #    # #    #     #  #     #  ##    #  #     #
#         #   #   #     #  #     #  # #   #  #     #
#  ####  #     #  ######   #     #  #  #  #  ######
#     #  #######  #   #    #     #  #   # #  #   #
#     #  #     #  #    #   #     #  #    ##  #    #
 #####   #     #  #     #  ######   #     #  #     #
""")


def main() -> None:
    logger.setup()

    parser, args = create_and_run_parser(sys.argv[1:])

    # default print help
    if len(sys.argv) == 1:
        parser.print_help()
        return

    if args.test:
        settings.TEST_MODE = True
        logger.enable_debugging()

    # wait to see if in test mode to initialize the database
    models.initialize_db()

    reflection.add_driver_path(settings.DRIVER_PATH)

    # execute the command
    args.func(args)


def _bound_to_bool(bound: str) -> bool:
    if bound == 'min':
        return False

    if bound == 'max':
        return True

    raise ValueError


def _bool_to_bound(upper_bound: bool) -> str:
    return 'max' if upper_bound else 'min'


def _power_to_bool(power: str) -> bool:
    if power == 'on':
        return True

    if power == 'off':
        return False

    raise ValueError


def _bool_to_power(powered_on: bool) -> str:
    return '[on]' if powered_on else '[off]' if powered_on is not None else ''


BOUND_INVALID_HELP = ('Invalid value for a bound, either specify min or'
                      ' max')
POWER_INVALID_HELP = ('Invalid value for power, either specify on or'
                      ' off')
NO_POWER_HELP = 'Power devices need the power argument specified'


def _copy_template(template_file: str, dest: Optional[str]) -> None:
    """
    Copies a given template file into a given destination file.
    If no file is given, uses the template file name and places
    the file in the current working directory.
    """

    gardnr_directory = os.path.dirname(os.path.abspath(__file__))
    template = ('{gardnr_directory}/{template_directory}/'
                '{template_file}').format(
                    gardnr_directory=gardnr_directory,
                    template_directory=settings.TEMPLATE_DIRECTORY,
                    template_file=template_file
                )

    if not dest:
        dest = '.'

    shutil.copy(template, dest)


def new_power(args: argparse.Namespace) -> None:
    _copy_template(settings.POWER_DRIVER_TEMPLATE, args.filename)


def new_sensor(args: argparse.Namespace) -> None:
    _copy_template(settings.SENSOR_DRIVER_TEMPLATE, args.filename)


def new_exporter(args: argparse.Namespace) -> None:
    _copy_template(settings.EXPORTER_DRIVER_TEMPLATE, args.filename)


def add_metric(args: argparse.Namespace) -> None:
    metric = models.Metric(id=uuid.uuid4(),
                           name=args.name,
                           topic=args.topic,
                           type=args.type,
                           manual=args.manual)
    metric.save(force_insert=True)

    print('{topic} {type} metric {name} added'.format(topic=metric.topic,
                                                      type=metric.type,
                                                      name=metric.name))


def add_driver(args: argparse.Namespace) -> None:
    # identify the driver
    driver_class = reflection.get_class_type(args.classname)

    driver_base = reflection.get_base_type(driver_class)

    driver = models.Driver(type=driver_base,
                           name=args.name,
                           fully_qualname=args.classname)

    if args.config is not None:
        driver.config = args.config

    driver.save()

    print('{type} driver {name} added'.format(type=driver_class,
                                              name=driver.name))


def add_schedule(args: argparse.Namespace) -> None:

    schedule = models.Schedule(
        name=args.name,
        minute=args.minute,
        hour=args.hour,
        day_of_month=args.day_of_month,
        month=args.month,
        day_of_week=args.day_of_week)

    if not args.yes:
        print('You entered: {}'.format(schedule.transcribe()))
        print('Does this look correct? ([y]/n)')
        answer = input()
        if answer == 'n':
            return

    schedule.save()

    print('schedule {} added'.format(schedule.name))


def add_trigger(args: argparse.Namespace) -> None:

    metric = models.Metric.get(models.Metric.name == args.metric)

    try:
        upper_bound = _bound_to_bool(args.bound)
    except ValueError:
        print(BOUND_INVALID_HELP)
        return

    power_driver = models.Driver.get(
        (models.Driver.name == args.driver) &
        (models.Driver.type == constants.POWER)
    )

    try:
        powered_on = _power_to_bool(args.power)
    except ValueError:
        print(POWER_INVALID_HELP)
        return

    models.Trigger.create(metric=metric,
                          upper_bound=upper_bound,
                          power_driver=power_driver,
                          power_on=powered_on)

    print('Trigger added for turning {driver} {power} when {metric} '
          'hits {bound} '.format(
              power=args.power,
              driver=args.driver,
              bound=args.bound,
              metric=args.metric))


def remove_metric(args: argparse.Namespace) -> None:
    metric = models.Metric.get(models.Metric.name == args.name)

    metric_logs = models.MetricLog.select().where(
        models.MetricLog.metric == metric)

    models.ExportLog.delete().where(
        models.ExportLog.metric_log.in_(metric_logs)).execute()

    models.MetricLog.delete().where(
        models.MetricLog.metric == metric).execute()

    metric.delete_instance()

    print('{name} metric removed'.format(name=metric.name))


def remove_driver(args: argparse.Namespace) -> None:
    driver = models.Driver.get(models.Driver.name == args.name)

    if driver.type == constants.EXPORTER:
        models.ExportLog.delete().where(
            models.ExportLog.driver == driver).execute()

    driver.delete_instance()

    print('{name} driver removed'.format(name=driver.name))


def remove_schedule(args: argparse.Namespace) -> None:
    schedule = models.Schedule.get(models.Schedule.name == args.name)

    models.DriverSchedule.delete().where(
        models.DriverSchedule.schedule == schedule).execute()

    schedule.delete_instance()

    print('{name} schedule removed'.format(name=schedule.name))


def remove_trigger(args: argparse.Namespace) -> None:
    try:
        upper_bound = _bound_to_bool(args.bound)
    except ValueError:
        print(BOUND_INVALID_HELP)
        return

    try:
        powered_on = _power_to_bool(args.power)
    except ValueError:
        print(POWER_INVALID_HELP)
        return

    trigger = models.Trigger.select()\
        .join(models.Driver)\
        .switch(models.Trigger)\
        .join(models.Metric)\
        .where((models.Trigger.power_on == powered_on) &
               (models.Driver.name == args.driver) &
               (models.Trigger.upper_bound == upper_bound) &
               (models.Metric.name == args.metric))\
        .get()

    trigger.delete_instance()

    print('Trigger removed for turning {driver} {power} when {metric} '
          'hits {bound} '.format(
              power=args.power,
              driver=args.driver,
              bound=args.bound,
              metric=args.metric))


def disable_metric(args: argparse.Namespace) -> None:
    metric = models.Metric.get(models.Metric.name == args.name)
    metric.disabled = True
    metric.save()

    print('{name} metric disabled'.format(name=metric.name))


def disable_driver(args: argparse.Namespace) -> None:
    driver = models.Driver.get(models.Driver.name == args.name)
    driver.disabled = True
    driver.save()

    print('{name} driver disabled'.format(name=driver.name))


def disable_schedule(args: argparse.Namespace) -> None:
    schedule = models.Schedule.get(models.Schedule.name == args.name)
    schedule.disabled = True
    schedule.save()

    print('{name} schedule disabled'.format(name=schedule.name))


def disable_trigger(args: argparse.Namespace) -> None:
    try:
        upper_bound = _bound_to_bool(args.bound)
    except ValueError:
        print(BOUND_INVALID_HELP)
        return

    trigger = models.Trigger.select()\
        .join(models.Metric)\
        .where((models.Metric.name == args.metric) &
               (models.Trigger.upper_bound == upper_bound))\
        .get()

    trigger.disabled = True
    trigger.save()

    print('Disabled {bound} trigger for {metric}'.format(
        bound=args.bound, metric=args.metric))


def enable_metric(args: argparse.Namespace) -> None:
    metric = models.Metric.get(models.Metric.name == args.name)
    metric.disabled = False
    metric.save()

    print('{name} metric enabled'.format(name=metric.name))


def enable_driver(args: argparse.Namespace) -> None:
    driver = models.Driver.get(models.Driver.name == args.name)
    driver.disabled = False
    driver.save()

    print('{name} driver enabled'.format(name=driver.name))


def enable_schedule(args: argparse.Namespace) -> None:
    schedule = models.Schedule.get(models.Schedule.name == args.name)
    schedule.disabled = False
    schedule.save()

    print('{name} schedule enabled'.format(name=schedule.name))


def enable_trigger(args: argparse.Namespace) -> None:
    try:
        upper_bound = _bound_to_bool(args.bound)
    except ValueError:
        print(BOUND_INVALID_HELP)
        return

    trigger = models.Trigger.select()\
        .join(models.Metric)\
        .where((models.Metric.name == args.metric) &
               (models.Trigger.upper_bound == upper_bound))\
        .get()

    trigger.disabled = False
    trigger.save()

    print('Enabled {bound} trigger for {metric}'.format(
        bound=args.bound, metric=args.metric))


def add_driver_schedule(args: argparse.Namespace) -> None:
    driver = models.Driver.get(models.Driver.name == args.driver)
    schedule = models.Schedule.get(models.Schedule.name == args.schedule)

    powered_on = None
    if driver.type == constants.POWER:
        if args.power:
            try:
                powered_on = _power_to_bool(args.power)
            except ValueError:
                print(POWER_INVALID_HELP)
                return
        else:
            print(NO_POWER_HELP)
            return

    models.DriverSchedule.create(
        driver=driver,
        schedule=schedule,
        power_on=powered_on
    )

    print('{driver} has been added to {schedule} '
          'which runs: {schedule_text}'.format(
              driver=driver.name,
              schedule=schedule.name,
              schedule_text=schedule.transcribe()
          ))


def remove_driver_schedule(args: argparse.Namespace) -> None:
    driver_schedule = models.DriverSchedule.select()\
            .join(models.Driver)\
            .switch(models.DriverSchedule)\
            .join(models.Schedule)\
            .where((models.Driver.name == args.driver) &
                   (models.Schedule.name == args.schedule))\
            .get()

    driver_schedule.delete_instance()

    print('{driver} has been removed from {schedule}'.format(
        driver=args.driver,
        schedule=args.schedule
    ))


def list_all(args: argparse.Namespace) -> None:
    del args

    print('Metrics: ')
    metrics = models.Metric.select()
    for metric in metrics:
        print('{name} {topic} {type} {manual} {disabled}'.format(
            name=metric.name,
            topic=metric.topic,
            type=metric.type,
            manual='(manual)' if metric.manual else '',
            disabled='(disabled)' if metric.disabled else ''))

    print('\nDrivers: ')
    for dt in constants.drivers:
        drivers = models.Driver.select().where(
            models.Driver.type == dt)

        if drivers:
            print('{type}s:'.format(type=dt))

            for driver in drivers:
                print('{name} {disabled}'.format(
                    name=driver.name,
                    disabled='(disabled)' if driver.disabled else ''))

    print('\nSchedules: ')
    schedules = models.Schedule.select()
    for schedule in schedules:
        print('{name} {schedule} drivers=({drivers}) {disabled}'.format(
            name=schedule.name,
            schedule=schedule.transcribe(),
            drivers=', '.join(['{name} {power}'.format(
                name=driverschedule.driver.name,
                power=_bool_to_power(driverschedule.power_on))
                               for driverschedule
                               in schedule.driver_schedules]),
            disabled='(disabled)' if schedule.disabled else ''
        ))

    print('\nTriggers: ')
    triggers = models.Trigger.select()
    for trigger in triggers:
        print('{metric} reaches {bound}, turn {driver} {power} '
              '{disabled}'.format(
                  metric=trigger.metric.name,
                  bound=_bool_to_bound(trigger.upper_bound),
                  driver=trigger.power_driver.name,
                  power='on' if trigger.power_on else 'off',
                  disabled='(disabled)' if trigger.disabled else ''
              ))


def grow_actions(args: argparse.Namespace) -> None:

    if args.action == 'start':
        try:
            grow.start()
        except grow.GrowAlreadyActiveError:
            print('There is a grow in progress,'
                  'end the current grow to start a new one')
    elif args.action == 'end':
        try:
            grow.end()
        except grow.NoActiveGrowError:
            print('There is no active grow to end')
    else:  # status
        active_grow = grow.get_active()

        if active_grow:
            grow_diff = datetime.utcnow() - active_grow.start
            print('It is currently day {num_days} of the grow'.format(
                num_days=grow_diff.days))

            stage = grow.get_current_stage(active_grow)
            if stage:
                print('Current grow stage is {stage}'.format(stage=stage))
        else:
            print('No active grow')


def manual_actions(args: argparse.Namespace) -> None:

    metric = models.Metric.get_or_none(
        models.Metric.name == args.metric_name)

    if not metric:
        print('{metric_name} metric does not exist'.format(
            metric_name=args.metric_name))
        return

    if metric.manual:
        if args.action == 'on':
            print('{metric_name} already has manual on'.format(
                metric_name=metric.name))
        else:
            metric.manual = False
            metric.save()
            print('{metric_name} set to manual off'.format(
                metric_name=metric.name))
    else:
        if args.action == 'off':
            print('{metric_name} already has manual off'.format(
                metric_name=metric.name))
        else:
            metric.manual = True
            metric.save()
            print('{metric_name} set to manual on'.format(
                metric_name=metric.name))


def read(args: argparse.Namespace) -> None:

    sensors = reflection.load_active_drivers(
        constants.SENSOR,
        args.include,
        args.exclude
    )

    tasks.read(sensors)


def write(args: argparse.Namespace) -> None:

    exporters = reflection.load_active_drivers(
        constants.EXPORTER,
        args.include,
        args.exclude
    )

    tasks.write(exporters)


def power_on(args: argparse.Namespace) -> None:
    power_devices = reflection.load_active_drivers(
        constants.POWER,
        args.drivers
    )

    tasks.power_on(power_devices)


def power_off(args: argparse.Namespace) -> None:
    power_devices = reflection.load_active_drivers(
        constants.POWER,
        args.drivers
    )

    tasks.power_off(power_devices)


class StoreDictKeyPair(argparse.Action):
    """
    Running: `./cli.py --key_pairs 1=2 foo=bar`
    Outputs: `argparse.Namespace(key_pairs={'1': '2', 'foo': 'bar'})`
    Credit: https://stackoverflow.com/a/42355279/1981635
    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        self._nargs = nargs
        super(StoreDictKeyPair, self).__init__(option_strings,
                                               dest,
                                               nargs=nargs,
                                               **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        key_pairs = {}

        for kv_str in values:
            key, value = kv_str.split('=')
            key_pairs[key] = value

        setattr(namespace, self.dest, key_pairs)


def create_parser() -> argparse.ArgumentParser:
    main_parser = argparse.ArgumentParser(
        description=LOGO,
        formatter_class=argparse.RawTextHelpFormatter
    )
    main_parser.add_argument('-t', '--test', action='store_true',
                             help='Run in test mode, no data will '
                             'be preserved')
    subparsers = main_parser.add_subparsers()

    new_parser = subparsers.add_parser('new', help='Create a new driver '
                                       'from a template')
    new_parser.set_defaults(func=lambda a: new_parser.print_help())
    new_subparsers = new_parser.add_subparsers()

    new_power_parser = new_subparsers.add_parser(
        'power',
        help='Add a driver for controlling powered devices'
    )
    new_power_parser.add_argument(
        'filename',
        nargs='?',
        help='name of the file to create, the default is {}'.format(
            settings.POWER_DRIVER_TEMPLATE)
    )
    new_power_parser.set_defaults(func=new_power)

    new_sensor_parser = new_subparsers.add_parser(
        'sensor',
        help='Add a sensor for logging sensor readings'
    )
    new_sensor_parser.add_argument(
        'filename',
        nargs='?',
        help='name of the file to create, the default is {}'.format(
            settings.SENSOR_DRIVER_TEMPLATE)
    )
    new_sensor_parser.set_defaults(func=new_sensor)

    new_exporter_parser = new_subparsers.add_parser(
        'exporter',
        help='Add an exporter for exporting logs'
    )
    new_exporter_parser.add_argument(
        'filename',
        nargs='?',
        help='name of the file to create, the default is {}'.format(
            settings.EXPORTER_DRIVER_TEMPLATE)
    )
    new_exporter_parser.set_defaults(func=new_exporter)

    add_parser = subparsers.add_parser('add',
                                       help='Add a metric, driver, schedule, '
                                       'or trigger')
    add_parser.set_defaults(func=lambda a: add_parser.print_help())
    add_subparsers = add_parser.add_subparsers()

    add_metric_parser = add_subparsers.add_parser('metric',
                                                  help='Add a metric')
    add_metric_parser.add_argument('topic', choices=[topic for topic in
                                                     constants.topics],
                                   help='Grouping topic of the metric')
    add_metric_parser.add_argument('type', choices=[metric for metric in
                                                    constants.metrics],
                                   help='The type of metric')
    add_metric_parser.add_argument('name', help='Description of the metric')
    add_metric_parser.add_argument('-m', '--manual', action='store_true',
                                   help='Set the metric as manual')
    add_metric_parser.set_defaults(func=add_metric)

    add_driver_parser = add_subparsers.add_parser('driver',
                                                  help='Add a driver')
    add_driver_parser.add_argument('name', help='Description of the driver')
    add_driver_parser.add_argument('classname',
                                   help='Fully qualified class name (e.g. '
                                   'mymodule.mysubmodule:MyClass)')
    add_driver_parser.add_argument('-c', '--config', dest='config',
                                   action=StoreDictKeyPair,
                                   nargs='+', metavar='KEY=VAL',
                                   help='configuration for the driver')
    add_driver_parser.set_defaults(func=add_driver)

    add_schedule_parser = add_subparsers.add_parser(
        'schedule',
        help='Create a CRON schedule, see https://en.wikipedia.org/wiki/Cron')
    add_schedule_parser.add_argument('name')
    add_schedule_parser.add_argument('minute')
    add_schedule_parser.add_argument('hour')
    add_schedule_parser.add_argument('day_of_month')
    add_schedule_parser.add_argument('month')
    add_schedule_parser.add_argument('day_of_week')
    add_schedule_parser.add_argument('-y', '--yes', action='store_true',
                                     help='Bypass confirmation')
    add_schedule_parser.set_defaults(func=add_schedule)

    add_trigger_parser = add_subparsers.add_parser(
        'trigger',
        help='Setup up a trigger for metric bound')
    add_trigger_parser.add_argument('metric', help='Name of the metric')
    add_trigger_parser.add_argument('bound',
                                    choices=['min', 'max'],
                                    help='Which bound the trigger is for')
    add_trigger_parser.add_argument('driver', type=str)
    add_trigger_parser.add_argument('power', type=str,
                                    choices=['on', 'off'])
    add_trigger_parser.set_defaults(func=add_trigger)

    remove_parser = subparsers.add_parser('remove',
                                          help='Removes a metric, driver '
                                          'schedule, or trigger')
    remove_parser.set_defaults(func=lambda a: remove_parser.print_help())
    remove_subparsers = remove_parser.add_subparsers()

    remove_metric_parser = remove_subparsers.add_parser('metric')
    remove_metric_parser.add_argument('name', type=str, help='Name of the '
                                      'metric to remove. Use the list command '
                                      'to see metric names')
    remove_metric_parser.set_defaults(func=remove_metric)

    remove_driver_parser = remove_subparsers.add_parser('driver')
    remove_driver_parser.add_argument('name', type=str, help='Name of the '
                                      'driver to remove. Use the list command '
                                      'to see driver names')
    remove_driver_parser.set_defaults(func=remove_driver)

    remove_schedule_parser = remove_subparsers.add_parser(
        'schedule',
        help='Remove a schedule')
    remove_schedule_parser.add_argument('name', type=str, help='Name of the '
                                        'schedule to remove. Use the list '
                                        'command to see schedule names')
    remove_schedule_parser.set_defaults(func=remove_schedule)

    remove_trigger_parser = remove_subparsers.add_parser('trigger')
    remove_trigger_parser.add_argument('metric', type=str)
    remove_trigger_parser.add_argument('bound', type=str,
                                       choices=['min', 'max'])
    remove_trigger_parser.add_argument('driver', type=str)
    remove_trigger_parser.add_argument('power', type=str,
                                    choices=['on', 'off'])
    remove_trigger_parser.set_defaults(func=remove_trigger)

    disable_parser = subparsers.add_parser('disable',
                                           help='Disables a metric, driver, '
                                           'schedule, or trigger')
    disable_parser.set_defaults(func=lambda a: disable_parser.print_help())
    disable_subparsers = disable_parser.add_subparsers()

    disable_metric_parser = disable_subparsers.add_parser(
        'metric',
        help='Disables a metric so it will not appear in the Log Entry Service'
    )
    disable_metric_parser.add_argument('name', type=str, help='Name of the '
                                       'metric to disable. Use the list '
                                       'command to see metric names')
    disable_metric_parser.set_defaults(func=disable_metric)

    disable_driver_parser = disable_subparsers.add_parser(
        'driver',
        help='Disables a driver so it will not be executed autonomously'
    )
    disable_driver_parser.add_argument('name', type=str, help='Name of the '
                                       'driver to disable. Use the list '
                                       'command to see driver names')
    disable_driver_parser.set_defaults(func=disable_driver)

    disable_schedule_parser = disable_subparsers.add_parser(
        'schedule',
        help='Disables a schedule so it will not be triggered')
    disable_schedule_parser.add_argument('name', type=str, help='Name of the '
                                         'schedule to disable. Use the list '
                                         'command to see schedule names')
    disable_schedule_parser.set_defaults(func=disable_schedule)

    disable_trigger_parser = disable_subparsers.add_parser('trigger')
    disable_trigger_parser.add_argument('metric', type=str, help='Name of the '
                                        'metric to disable. Use the list '
                                        'command to see schedule names')
    disable_trigger_parser.add_argument('bound', type=str,
                                        choices=['min', 'max'])
    disable_trigger_parser.set_defaults(func=disable_trigger)

    enable_parser = subparsers.add_parser('enable',
                                          help='Enables a metric, driver, '
                                          'schedule, or trigger')
    enable_parser.set_defaults(func=lambda a: enable_parser.print_help())
    enable_subparsers = enable_parser.add_subparsers()

    enable_metric_parser = enable_subparsers.add_parser(
        'metric',
        help='Enables a metric so it will appear in the Log Entry Service, if '
        'set to manual'
    )
    enable_metric_parser.add_argument('name', type=str, help='Name of the '
                                      'metric to enable. Use the list '
                                      'command to see metric names')
    enable_metric_parser.set_defaults(func=enable_metric)

    enable_driver_parser = enable_subparsers.add_parser(
        'driver',
        help='Enables a driver so it will be executed autonomously'
    )
    enable_driver_parser.add_argument('name', type=str, help='Name of the '
                                      'driver to enable. Use the list '
                                      'command to see driver names')
    enable_driver_parser.set_defaults(func=enable_driver)

    enable_schedule_parser = enable_subparsers.add_parser(
        'schedule',
        help='Enables a schedule so it will be triggered'
    )
    enable_schedule_parser.add_argument('name', type=str, help='Name of the '
                                        'schedule to enable. Use the list '
                                        'command to see schedule names')
    enable_schedule_parser.set_defaults(func=enable_schedule)

    enable_trigger_parser = enable_subparsers.add_parser('trigger')
    enable_trigger_parser.add_argument('metric', type=str, help='Name of the '
                                       'metric to enable. Use the list '
                                       'command to see schedule names')
    enable_trigger_parser.add_argument('bound', type=str,
                                       choices=['min', 'max'])
    enable_trigger_parser.set_defaults(func=enable_trigger)

    schedule_parser = subparsers.add_parser('schedule',
                                            help='Attach a driver to a '
                                            'schedule')
    schedule_parser.set_defaults(func=lambda a: schedule_parser.print_help())
    schedule_subparsers = schedule_parser.add_subparsers()

    schedule_driver_help = ('Name of driver. Use the list command to see '
                            'driver names')
    schedule_schedule_help = ('Name of scheduler. Use the list command to see '
                              'schedule names')

    schedule_add_parser = schedule_subparsers.add_parser(
        'add',
        help='Add a driver to a schedule'
    )
    schedule_add_parser.add_argument(
        'driver',
        type=str,
        help=schedule_driver_help
    )
    schedule_add_parser.add_argument(
        'schedule',
        type=str,
        help=schedule_schedule_help
    )
    schedule_add_parser.add_argument(
        'power',
        type=str,
        nargs='?',
        choices=['on', 'off'],
        help='Only used for scheduling power drivers, accepts either on or off'
    )
    schedule_add_parser.set_defaults(func=add_driver_schedule)

    schedule_remove_parser = schedule_subparsers.add_parser(
        'remove',
        help='Remove a driver from a schedule'
    )
    schedule_remove_parser.add_argument(
        'driver',
        type=str,
        help=schedule_driver_help
    )
    schedule_remove_parser.add_argument(
        'schedule',
        type=str,
        help=schedule_schedule_help
    )
    schedule_remove_parser.set_defaults(func=remove_driver_schedule)

    list_parser = subparsers.add_parser('list', help='Lists the metrics with '
                                        'their global IDs, drivers, '
                                        'schedules, and triggers')
    list_parser.set_defaults(func=list_all)

    grow_parser = subparsers.add_parser('grow',
                                        help='Manages the start and end '
                                        'of a grow')
    grow_parser.add_argument('action', choices=['start', 'end', 'status'])
    grow_parser.set_defaults(func=grow_actions)

    manual_parser = subparsers.add_parser('manual',
                                          help=("Change a metric's "
                                                'manual state'))
    manual_parser.add_argument('action', choices=['on', 'off'])
    manual_parser.add_argument('metric_name',
                               help='name of the metric')
    manual_parser.set_defaults(func=manual_actions)

    drivers_include_help = 'Optional list of specific driver to include.'
    drivers_exclude_help = 'Optional list of specific driver to exclude.'

    read_parser = subparsers.add_parser(
        'read',
        help=('Read sensors. If no include of exclude lists are provided, '
              'reads all sensor drivers')
    )
    read_parser.add_argument('-i', '--include', type=str, nargs='+',
                             help=drivers_include_help)
    read_parser.add_argument('-e', '--exclude', type=str, nargs='+',
                             help=drivers_exclude_help)
    read_parser.set_defaults(func=read)

    write_parser = subparsers.add_parser(
        'write',
        help=('Run exporters. If no include of exclude lists are provided, '
              'run all exporters')
    )
    write_parser.add_argument('-i', '--include', type=str, nargs='+',
                              help=drivers_include_help)
    write_parser.add_argument('-e', '--exclude', type=str, nargs='+',
                              help=drivers_exclude_help)
    write_parser.set_defaults(func=write)

    power_parser = subparsers.add_parser('power',
                                         help='Toggle power driver on or off')
    power_parser.set_defaults(func=lambda a: power_parser.print_help())
    power_subparsers = power_parser.add_subparsers()

    power_drivers_help = 'One or more driver names'

    power_on_parser = power_subparsers.add_parser('on',
                                                  help='Powers on drivers')
    power_on_parser.add_argument('drivers', type=str, nargs='+',
                                 help=power_drivers_help)
    power_on_parser.set_defaults(func=power_on)

    power_off_parser = power_subparsers.add_parser('off',
                                                   help='Powers off drivers')
    power_off_parser.add_argument('drivers', type=str, nargs='+',
                                  help=power_drivers_help)
    power_off_parser.set_defaults(func=power_off)

    return main_parser


def create_and_run_parser(
        cli_args: List
) -> (Tuple[argparse.ArgumentParser, argparse.Namespace]):
    parser = create_parser()
    return parser, parser.parse_args(cli_args)


if __name__ == '__main__':
    main()
