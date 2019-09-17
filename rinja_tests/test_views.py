import pytest


@pytest.mark.django_db
def test_retrieve_all_stocks(client):
    response = client.get('/stocks')
    print(response.content)
