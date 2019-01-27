from grow_recipe.constants import *  # noqa F403

NOTES = 'notes'
IMAGE = 'image'
POWER = 'power'
GARDNR_METRICS = {'notes', 'image', 'power'}
metrics = metrics.union(GARDNR_METRICS)

MANUAL_OVERRIDE_CONFIG = 'manual'


SENSOR = 'sensor'
POWER = 'power'
EXPORTER = 'exporter'
drivers = {SENSOR, POWER, EXPORTER}


CELSIUS = 'c'
FAHRENHEIT = 'f'
t9e_untis = {CELSIUS, FAHRENHEIT}
