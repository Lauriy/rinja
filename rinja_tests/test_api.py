# @mock.patch('django.core.cache.cache.get')
# def test_retrieve_all_stocks(mocked_cache, client):
#     mocked_cache.return_value = [
#         {'Ticker': 'TEST1', 'Name': 'Test stonk', 'ISIN': 'LT0000000000', 'MarketPlace': 'VLN',
#          'List/segment': 'Baltic Main List', 'Currency': 'EUR'}
#     ]
#     response = client.get('/api/v1/stocks/')
#
#     assert response.status_code == 200
#
#
# def test_unauthenticated_watchlist_retrieval(client):
#     response = client.get('/api/v1/stocks/?watchlist=true')
#
#     assert response.status_code == 401
#
#
# @pytest.mark.django_db
# def test_authenticated_watchlist_retrieval(client):
#     response = client.get('/api/v1/stocks/?watchlist=true')
#
#     assert response.status_code == 200
