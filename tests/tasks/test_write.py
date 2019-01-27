from typing import List
from uuid import uuid4

import pytest

from gardnr import constants, drivers, models, tasks
from tests import utils


@pytest.mark.usefixtures('test_env')
def test_export_basic():
    """Test export a single log"""

    sensor = utils.create_and_load_air_temperature_sensor()

    tasks.read([sensor])

    exporter = utils.create_and_load_exporter()

    export_logs1 = models.ExportLog.select()
    assert export_logs1.count() == 0
    assert utils.MockExporter.call_count == 0

    tasks.write([exporter])

    export_logs2 = models.ExportLog.select()
    assert export_logs2.count() == 1
    assert utils.MockExporter.call_count == 1


@pytest.mark.usefixtures('test_env')
def test_export_missing_records():
    """
    You need to join to the relationship model whose attributes are being
    selected
    """

    sensor = utils.create_and_load_air_temperature_sensor()
    exporter = utils.create_and_load_exporter()

    tasks.read([sensor])
    tasks.write([exporter])

    export_logs1 = models.ExportLog.select()
    assert export_logs1.count() == 1
    assert utils.MockExporter.call_count == 1

    tasks.read([sensor])
    tasks.write([exporter])

    export_logs2 = models.ExportLog.select()
    assert export_logs2.count() == 2
    assert utils.MockExporter.call_count == 2


@pytest.mark.usefixtures('test_env')
def test_export_new_exporter():

    sensor = utils.create_and_load_air_temperature_sensor()

    tasks.read([sensor])

    exporter = utils.create_and_load_exporter()

    export_logs1 = models.ExportLog.select()
    assert export_logs1.count() == 0
    assert utils.MockExporter.call_count == 0

    tasks.write([exporter])

    export_logs2 = models.ExportLog.select()
    assert export_logs2.count() == 1
    assert utils.MockExporter.call_count == 1

    exporter2 = utils.create_and_load_exporter('new-exporter')

    tasks.write([exporter, exporter2])

    export_logs3 = models.ExportLog.select()
    assert export_logs3.count() == 2
    assert utils.MockExporter.call_count == 2


class FailingExporterSpecify(drivers.Exporter):
    def export(self, logs: List[models.MetricLog]) -> None:
        e = Exception()
        e.failed_logs = [logs[0]]
        raise e


@pytest.mark.usefixtures('test_env')
def test_export_failed_specify():

    sensor = utils.create_and_load_air_temperature_sensor()

    tasks.read([sensor])
    tasks.read([sensor])

    exporter = utils.create_and_load_exporter(
        driver_type=FailingExporterSpecify)

    tasks.write([exporter])

    export_logs = models.ExportLog.select()
    assert export_logs.count() == 1


class FailingExporterAll(drivers.Exporter):
    def export(self, logs: List[models.MetricLog]) -> None:
        raise Exception()


@pytest.mark.usefixtures('test_env')
def test_export_failed_all():

    sensor = utils.create_and_load_air_temperature_sensor()

    tasks.read([sensor])

    exporter = utils.create_and_load_exporter(driver_type=FailingExporterAll)

    tasks.write([exporter])

    export_logs = models.ExportLog.select()
    assert export_logs.count() == 0


class WhitelistExporter(utils.MockExporter):
    whitelist = [constants.HUMIDITY]


@pytest.mark.usefixtures('test_env')
def test_whitelisted_write():

    temp_metric = utils.create_air_temperature_metric()
    models.MetricLog.create(id=uuid4(), metric=temp_metric, value=0)

    humid_metric = models.Metric.create(id=uuid4(),
                                        name='test-humidity',
                                        topic=constants.AIR,
                                        type=constants.HUMIDITY)
    whitelisted_log = models.MetricLog.create(id=uuid4(),
                                              metric=humid_metric,
                                              value=0)

    whitelist_exporter = utils.create_and_load_exporter('whitelist-exporter',
                                                        WhitelistExporter)

    tasks.write([whitelist_exporter])

    export_logs = models.ExportLog.select()
    assert export_logs.count() == 1
    assert export_logs[0].metric_log.id == whitelisted_log.id


class BlacklistExporter(utils.MockExporter):
    blacklist = [constants.HUMIDITY]


@pytest.mark.usefixtures('test_env')
def test_blacklisted_write():

    temp_metric = utils.create_air_temperature_metric()
    models.MetricLog.create(id=uuid4(), metric=temp_metric, value=0)

    humid_metric = models.Metric.create(id=uuid4(),
                                        name='test-humidity',
                                        topic=constants.AIR,
                                        type=constants.HUMIDITY)
    blacklisted_log = models.MetricLog.create(id=uuid4(),
                                              metric=humid_metric,
                                              value=0)

    blacklist_exporter = utils.create_and_load_exporter('blacklist-exporter',
                                                        BlacklistExporter)

    tasks.write([blacklist_exporter])

    export_logs = models.ExportLog.select()
    assert export_logs.count() == 1
    assert export_logs[0].metric_log.id != blacklisted_log.id
