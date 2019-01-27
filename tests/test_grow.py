import pytest

from gardnr import grow, models


@pytest.mark.usefixtures('test_env')
def test_start_grow():

    active_grow1 = grow.get_active()
    assert not active_grow1

    grow.start()

    active_grow2 = grow.get_active()
    assert active_grow2


@pytest.mark.usefixtures('test_env')
def test_start_already_active():

    grow.start()

    active_grow1 = grow.get_active()
    assert active_grow1

    with pytest.raises(grow.GrowAlreadyActiveError):
        grow.start()

    assert models.Grow.select().count() == 1


@pytest.mark.usefixtures('test_env')
def test_end_grow():

    grow.start()

    active_grow1 = grow.get_active()
    assert active_grow1

    grow.end()

    active_grow2 = grow.get_active()
    assert not active_grow2


@pytest.mark.usefixtures('test_env')
def test_end_no_active():

    with pytest.raises(grow.NoActiveGrowError):
        grow.end()


@pytest.mark.usefixtures('test_env')
def test_new_grow():

    grow.start()
    grow1 = grow.get_active()
    grow.end()

    grow.start()
    grow2 = grow.get_active()

    assert models.Grow.select().count() == 2

    assert grow1.id != grow2.id
