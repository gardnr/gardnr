# pylint: disable=protected-access
from unittest.mock import patch

import pytest
import grow_recipe

from gardnr import automata, grow, metrics, reflection
from tests import utils


@pytest.mark.usefixtures('test_env')
def test_build_trigger_bounds() -> None:
    trigger = utils.create_air_temperature_metric_trigger()

    grow.start()
    active_grow = grow.get_active()

    assert automata.trigger_bounds == []

    test_max = 0
    with patch('grow_recipe.get_metric',
               return_value=
               grow_recipe.query.find_metric_value.Metric(None, test_max)):

        automata._build_trigger_bounds(active_grow, None)

    assert len(automata.trigger_bounds) == 1
    assert automata.trigger_bounds[0].trigger.metric.id == trigger.metric.id
    assert automata.trigger_bounds[0].bound == test_max


@pytest.mark.usefixtures('test_env')
def test_bound_checker():
    test_min_bound = 0

    trigger = utils.create_air_temperature_metric_trigger(
        trigger_upper_bound=False, power_on=False)

    power_driver = reflection.load_driver(trigger.power_driver)

    automata.trigger_bounds.append(
        automata.TriggerBound(trigger, test_min_bound, power_driver))

    metrics.create_metric_log(trigger.metric.name, test_min_bound-1)

    assert utils.MockPower.off_count == 0
    automata.bound_checker()
    assert utils.MockPower.off_count == 1


@pytest.mark.usefixtures('test_env')
def test_active_bound_checker():
    test_min_bound = 0

    trigger = utils.create_air_temperature_metric_trigger(
        power_driver_type=utils.MockPower,
        trigger_upper_bound=False,
        power_on=False
    )

    power_driver = reflection.load_driver(trigger.power_driver)

    automata.active_trigger_bounds.append(
        automata.TriggerBound(trigger, test_min_bound, power_driver))

    metrics.create_metric_log(trigger.metric.name, test_min_bound)

    assert utils.MockPower.on_count == 0
    automata.bound_checker()
    assert utils.MockPower.on_count == 1
