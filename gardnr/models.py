"""Driver and log models."""
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List

import cron_descriptor
from peewee import (BlobField, BooleanField, DateTimeField, FloatField,
                    ForeignKeyField, Model, ModelSelect, SqliteDatabase,
                    TextField, UUIDField)

from gardnr import constants, settings

# initialize with None so run-time variables can be used
# set the connection string, reference: https://goo.gl/ms2oHP
_db = SqliteDatabase(None)


def initialize_db() -> None:
    """
    Creates any missing tables in the database
    """

    if settings.TEST_MODE:
        _db.init(':memory:')
    else:
        _db.init(settings.LOCAL_DB)

    # incase there is a connection issue it will be found here
    # instead of downstream
    _db.connect()

    _db.create_tables(BaseModel.__subclasses__(), safe=True)


class BaseModel(Model):
    class Meta:
        database = _db


class JSONField(TextField):

    def db_value(self, value: Dict) -> str:
        return json.dumps(value)

    def python_value(self, value: Optional[str]) -> Optional[Dict]:
        if value is not None:
            return json.loads(value)
        return None


class Metric(BaseModel):

    id = UUIDField(primary_key=True)
    name = TextField(unique=True)

    topic = TextField(choices=[(topic, topic)
                               for topic in constants.topics])
    type = TextField(choices=[(metric, metric)
                              for metric in constants.metrics])

    manual = BooleanField(default=False)

    disabled = BooleanField(default=False)

    def get_latest_log(
            self,
            cutoff: Optional[timedelta] = None
    ) -> Optional['MetricLog']:
        """
        Returns the latest log for a given log. Optionally, provide a
        cutoff date for the latest the log can be from.
        """

        latest_log = MetricLog.select()\
            .join(Metric)\
            .where(Metric.name == self.name)\
            .order_by(MetricLog.timestamp.desc())\
            .limit(1)

        if cutoff:
            latest_log = latest_log.where(
                MetricLog.timestamp >= datetime.utcnow() - cutoff)

        if not latest_log:
            return None

        return latest_log[0]


class Driver(BaseModel):
    """
    Information about a device.

    Config holds information on how to access data from the device.
    It can be customized
    """

    name = TextField(unique=True)
    type = TextField(choices=[(driver, driver)
                              for driver in constants.drivers])
    fully_qualname = TextField()

    config = JSONField(null=True)

    disabled = BooleanField(default=False)


class Schedule(BaseModel):
    """
    cron-style schedule to execute drivers on
    """

    name = TextField(unique=True)

    disabled = BooleanField(default=False)

    minute = TextField()
    hour = TextField()
    day_of_month = TextField()
    month = TextField()
    day_of_week = TextField()

    @property
    def crontab(self):
        """
        Converts model fields to crontab syntax
        """
        return ('{minute} {hour} {day_of_month} '
                '{month} {day_of_week}').format(
                    minute=self.minute,
                    hour=self.hour,
                    day_of_month=self.day_of_month,
                    month=self.month,
                    day_of_week=self.day_of_week)

    def transcribe(self) -> str:
        """
        converts crontab syntax to english
        """
        return cron_descriptor.get_description(self.crontab)


class DriverSchedule(BaseModel):
    """
    Many-to-many relationship between drivers and schedules
    peewee docs: https://goo.gl/8SB4iY
    """

    driver = ForeignKeyField(Driver)
    schedule = ForeignKeyField(Schedule, backref='driver_schedules')

    # used for power devices to be either turned on or off
    power_on = BooleanField(null=True, default=None)


class MetricLog(BaseModel):
    id = UUIDField(primary_key=True)

    timestamp = DateTimeField(default=datetime.utcnow)

    longitude = FloatField(null=True)
    latitude = FloatField(null=True)
    elevation = FloatField(null=True)

    value = BlobField()

    metric = ForeignKeyField(Metric)


class ExportLog(BaseModel):
    """
    Many-to-many relationship which logs occurrences of metric logs being
    exported
    """

    metric_log = ForeignKeyField(MetricLog)
    driver = ForeignKeyField(Driver)


class Trigger(BaseModel):
    """
    A rule for what power device to either turn on or off a when a metric's
    value hits either an upper or lower bound (too_high)
    """

    metric = ForeignKeyField(Metric)
    # either the upper bound or lower bound for the metric
    upper_bound = BooleanField()

    power_driver = ForeignKeyField(Driver)
    # either turn on or off for the power driver
    power_on = BooleanField()

    disabled = BooleanField(default=False)


class Grow(BaseModel):
    id = UUIDField(primary_key=True)

    start = DateTimeField(default=datetime.utcnow)
    end = DateTimeField(null=True)
