import pytest

from gardnr import models, tasks
from tests import utils


@pytest.mark.usefixtures('test_env')
def test_power_on():

    power_device = utils.create_and_load_power_device()

    assert power_device.on_count == 0

    tasks.power_on([power_device])

    assert power_device.on_count == 1


@pytest.mark.usefixtures('test_env')
def test_power_off():

    power_device = utils.create_and_load_power_device()

    assert power_device.off_count == 0

    tasks.power_off([power_device])

    assert power_device.off_count == 1
