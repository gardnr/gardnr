import pytest

from gardnr import models, tasks
from tests import utils


@pytest.mark.usefixtures('test_env')
def test_read_sensor():
    """basic test for reading a mock sensor."""

    sensor = utils.create_and_load_air_temperature_sensor()

    tasks.read([sensor])

    logs = models.MetricLog.select()

    assert logs.count() == 1
    assert logs[0].metric.name == utils.TEST_METRIC
    assert logs[0].value == utils.TEST_TEMPERATURE
