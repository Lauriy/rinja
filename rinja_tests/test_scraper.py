import os
from unittest import mock

import bs4
import pytest
import requests
from django.core.files.base import ContentFile

from rinja.scraper import Scraper


@mock.patch.object(requests, 'get')
def test_retrieve_general_market_data(mocked_get: object):
    scraper = Scraper()
    mockresponse = mock.Mock()
    mocked_get.return_value = mockresponse
    with open('/'.join([os.path.dirname(os.path.realpath(__file__)), 'fixtures/shares_20190916.xlsx']), 'rb') as f:
        response = f.read()
    mockresponse.content = response
    result = scraper.retrieve_general_market_data()
    assert len(result) == 70
    for stock in result:
        assert stock['Ticker']

@pytest.mark.parametrize(('captcha_page_response_file', 'image_response_file', 'vision_response'), [
    ('captcha_page_response_72eefe4c2308be33e9c902ce293a2d53.html', 'captcha_image_response_w92e.png'),
    ('captcha_page_response_72eefe4c2308be33e9c902ce293a2d53.html', 'captcha_image_response_w92e.png'),
    ('captcha_page_response_72eefe4c2308be33e9c902ce293a2d53.html', 'captcha_image_response_w92e.png')
])
@mock.patch.object(Scraper.google_vision_client, 'text_detection')
def test_retrieve_captcha_candidate(mocked_text_detection, captcha_page_response_file, image_response_file, vision_response):
    scraper = Scraper()
    result = scraper.retrieve_4_letter_captcha_candidate()


# def test_capture_data():
#     response1 = requests.get('https://nasdaqcsd.com/statistics/en/shareholders')
#     with open('response1.html', 'w') as f:
#         f.write(response1.text)
#     soup = bs4.BeautifulSoup(response1.text, 'html.parser')
#     captcha_id = soup.select('#captcha-id')[0]['value']
#     captcha_image_url = f'https://nasdaqcsd.com/statistics/graphics/captcha/{captcha_id}.png'
#     image_content = requests.get(captcha_image_url).content
#     with open('response2.png', 'wb') as f:
#         f.write(image_content)
