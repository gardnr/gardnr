import pytest


@pytest.mark.skip('Not setup to work yet')
@pytest.mark.usefixture('test_env')
def test_manual_metric(web_client):
    rv = web_client.get('/')
    print(rv.data)
