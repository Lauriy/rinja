from typing import Optional

import bs4
import requests
import xlrd
from django.core.files.base import ContentFile
from google.cloud import vision
from google.cloud.vision import types


class Scraper:
    # Cache
    google_vision_client = None

    @staticmethod
    def retrieve_general_market_data():
        # Data comes with 15 minutes of delay
        # url = f'https://www.nasdaqbaltic.com/statistics/en/shares?download=1&date={year}-{month}-{day}'
        url = f'https://www.nasdaqbaltic.com/statistics/en/shares?download=1'
        response = requests.get(url)
        parsed = xlrd.open_workbook(file_contents=response.content)
        worksheet = parsed.sheet_by_index(0)
        keys = worksheet.row_values(0)
        values = [worksheet.row_values(i) for i in range(1, worksheet.nrows)]
        dict_list = []
        for value in values:
            for inner_key, inner_value in enumerate(value):
                if inner_value == '':
                    # This would cause so many headaches down the line otherwise
                    value[inner_key] = None
            dict_list.append(dict(zip(keys, value)))

        return dict_list

    def retrieve_4_letter_captcha_candidate(self) -> (str, str, str, ContentFile):
        captcha_id, captcha_input, session_id, image_content = None, None, None, None
        captcha_retrieval_url = 'https://nasdaqcsd.com/statistics/en/shareholders'
        if not self.google_vision_client:
            self.google_vision_client = vision.ImageAnnotatorClient()
        while not captcha_input or len(captcha_input) != 4:
            print('Trying to retrieve 4-letter CAPTCHA answer...')
            captcha_page = requests.get(captcha_retrieval_url)
            try:
                session_id = captcha_page.cookies['PHPSESSID']
            except KeyError:  # Happens sometimes
                continue
            soup = bs4.BeautifulSoup(captcha_page.text, 'html.parser')
            captcha_id = soup.select('#captcha-id')[0]['value']
            captcha_image_url = f'https://nasdaqcsd.com/statistics/graphics/captcha/{captcha_id}.png'
            image_content = requests.get(captcha_image_url).content
            image_to_run_vision_on = types.Image(content=image_content)
            vision_response = self.google_vision_client.text_detection(image=image_to_run_vision_on)
            print(vision_response.text_annotations)
            try:
                captcha_input = vision_response.text_annotations[0].description.strip()
            except IndexError:
                continue
        content_file = ContentFile(image_content)

        return captcha_id, captcha_input, session_id, content_file

    @staticmethod
    def retrieve_holding_data_using_captcha(stock_isin: str, captcha_id: str, captcha_input: str,
                                            session_id: str) -> Optional[bs4.BeautifulSoup]:
        print(f'Trying CAPTCHA with answer {captcha_input} on stock {stock_isin} with session ID {session_id}')
        holdings_url = f'https://nasdaqcsd.com/statistics/et/shareholders?security={stock_isin}&captcha[id]=' \
                       f'{captcha_id}&captcha[input]={captcha_input}'
        holdings_response = requests.get(holdings_url, cookies=dict(PHPSESSID=session_id))
        holdings_soup = bs4.BeautifulSoup(holdings_response.text, 'html.parser')
        tables = holdings_soup.select('.table-striped')
        if not len(tables):
            print(f'{len(tables)} is not enough tables')
            return None

        return holdings_soup
