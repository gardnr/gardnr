from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from gardnr import models
from tests import utils


@pytest.mark.usefixtures('test_env')
def test_get_latest_log():
    metric = utils.create_air_temperature_metric()

    assert not metric.get_latest_log()
    assert not metric.get_latest_log(timedelta(minutes=1))

    models.MetricLog.create(id=uuid4(),
                            timestamp=datetime(1970, 1, 1),
                            metric=metric,
                            value=0)

    log = models.MetricLog.create(id=uuid4(),
                                  timestamp=datetime(1988, 5, 5),
                                  metric=metric,
                                  value=0)

    latest_log1 = metric.get_latest_log()
    assert latest_log1
    assert latest_log1.id == log.id

    assert not metric.get_latest_log(timedelta(minutes=1))
