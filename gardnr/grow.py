from datetime import datetime
from typing import Optional, TextIO
from uuid import uuid4

import grow_recipe

from gardnr import models, settings


class GrowAlreadyActiveError(Exception):
    pass


class NoActiveGrowError(Exception):
    pass


def get_active() -> Optional[models.Grow]:
    """
    Returns a grow that is currently in progress,
    A grow in progress is one with an 'end' set to NULL
    """
    # pylint: disable=singleton-comparison
    return models.Grow.get_or_none(models.Grow.end == None)  # noqa: E711


def get_tracked_grow() -> Optional[models.Grow]:
    """
    Only returns the active grow if there is recipe set
    """
    if settings.GROW_RECIPE:
        return get_active()

    return None


def get_current_stage(active_grow: models.Grow) -> Optional[str]:

    if settings.GROW_RECIPE:
        with open(settings.GROW_RECIPE) as recipe:
            return grow_recipe.get_grow_stage(recipe, active_grow.start)

    return None


def get_metric_bound(
        recipe: TextIO,
        tracked_grow: models.Grow,
        metric_topic: str,
        metric_type: str
) -> Optional[grow_recipe.query.find_metric_value.Metric]:
    return grow_recipe.get_metric(
        recipe, metric_topic, metric_type, tracked_grow.start)


def start() -> None:
    if get_active():
        raise GrowAlreadyActiveError()

    models.Grow.create(id=uuid4())


def end() -> None:
    active_grow = get_active()

    if not active_grow:
        raise NoActiveGrowError()

    active_grow.end = datetime.utcnow()
    active_grow.save()
