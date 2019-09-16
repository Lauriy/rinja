import os
from unittest import mock

import requests

from rinja.scraper import retrieve_general_market_data_for_date


@mock.patch.object(requests, 'get')
def test_retrieve_general_market_data_for_date(mocked_get):
    mockresponse = mock.Mock()
    mocked_get.return_value = mockresponse
    with open('/'.join([os.path.dirname(os.path.realpath(__file__)), 'fixtures/shares_20190916.xlsx']), 'rb') as f:
        response = f.read()
    mockresponse.content = response
    result = retrieve_general_market_data_for_date(2019, 9, 16)
    assert len(result) == 70
    for stock in result:
        assert stock['Ticker']

# @mock.patch.object(requests, 'get')
# def test_scrape_general_market_data_for_given_date(mocked_get):
#     mockresponse = mock.Mock()
#     mocked_get.return_value = mockresponse
#     with open('/'.join([os.path.dirname(os.path.realpath(__file__)), 'fixtures/all-stocks-scraped-page.txt'])) as f:
#         scrape_response = f.read()
#     mockresponse.text = scrape_response
#     result = scrape_general_market_data_for_date(2019, 9, 16)
