import logging
import os

from gardnr import constants

# when TEST_MODE is enabled, data is stored in a temporary in-memory database
TEST_MODE = False

LOCAL_DB = 'gardnr.db'
DRIVER_PATH = os.getcwd()

# logging
LOG_FILE = 'gardnr.log'
LOG_LEVEL = logging.INFO
LOG_FILE_SIZE = 10485760  # 10MB
LOG_FILE_COUNT = 1

UPLOAD_PATH = 'uploaded'

# l10n
TEMPERATURE_UNIT = constants.CELSIUS

GROW_RECIPE = None
BOUND_CHECK_FREQUENCY = 5  # in minutes

# can be overwritten incase there are more verbose templates
TEMPLATE_DIRECTORY = 'templates'
SENSOR_DRIVER_TEMPLATE = 'sensor_driver.py'
EXPORTER_DRIVER_TEMPLATE = 'exporter_driver.py'
POWER_DRIVER_TEMPLATE = 'power_driver.py'

try:
    # flake8: noqa
    # pylint: disable=wildcard-import
    from settings_local import *  # type: ignore
except ImportError:
    pass
