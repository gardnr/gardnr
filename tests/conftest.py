import pytest

from gardnr import automata, models, server, settings
from tests import utils


@pytest.fixture(scope='function')
def test_env():
    """Sets up environment for testing"""
    settings.TEST_MODE = True

    # reinitialized an empty database in memory
    models.initialize_db()

    # reset test exporter call count
    utils.MockExporter.call_count = 0

    utils.MockPower.on_count = 0
    utils.MockPower.off_count = 0

    automata.trigger_bounds = []
    automata.active_trigger_bounds = []


@pytest.fixture
def web_client():
    # TODO: needs to be setup to use in-memory database
    # http://flask.pocoo.org/docs/1.0/testing/
    client = server.app.test_client()

    yield client
