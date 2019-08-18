import datetime
import re

import bs4
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from google.cloud import vision
from google.cloud.vision import types
from nameparser import HumanName

from rinja.models import Stock, Captcha, StockPosition
from django.conf import settings

class Command(BaseCommand):
    help = 'Scrapes all stocks - intended to be run daily'

    def handle(self, *args, **options):
        all_supported_stocks = Stock.objects.all()
        # TODO: Maybe use /en/ URL?
        captcha_retrieval_url = 'https://nasdaqcsd.com/statistics/et/shareholders'
        stock = Stock.objects.filter(pk=8).first()
        with open('last_result.txt', 'r') as f:
            holdings_soup = bs4.BeautifulSoup(f.read(), 'html.parser')
            shareholder_rows = holdings_soup.select('.most-numbers')[0].select('tbody')[0].select('tr')
            now = datetime.datetime.now()
            for shareholder_row in shareholder_rows:
                shareholder_columns = shareholder_row.select('td')
                name = shareholder_columns[0].decode_contents()
                amount = int(re.sub(r'\s+', '', shareholder_columns[1].decode_contents(), flags=re.UNICODE))
                StockPosition(
                    stock=stock,
                    holder=name,
                    amount=amount,
                    at_date=now - datetime.timedelta(days=settings.STOCK_HOLDING_REPORT_DELAY_DAYS)
                ).save()

        # google_vision_client = vision.ImageAnnotatorClient()
        # for stock in all_supported_stocks:
        #     shareholders_retrieved = False
        #     while shareholders_retrieved is False:
        #         captcha_input = None
        #         while not captcha_input or len(captcha_input) != 4:
        #             print('Trying to retrieve 4-letter CAPTCHA answer...')
        #             captcha_page = requests.get(captcha_retrieval_url)
        #             session_id = captcha_page.cookies['PHPSESSID']
        #             soup = bs4.BeautifulSoup(captcha_page.text, 'html.parser')
        #             captcha_id = soup.select('#captcha-id')[0]['value']
        #             captcha_image_url = f'https://nasdaqcsd.com/statistics/graphics/captcha/{captcha_id}.png'
        #             image_content = requests.get(captcha_image_url).content
        #             image_to_run_vision_on = types.Image(content=image_content)
        #             vision_response = google_vision_client.text_detection(image=image_to_run_vision_on)
        #             try:
        #                 captcha_input = vision_response.text_annotations[0].description.strip()
        #             except IndexError:
        #                 continue
        #         print('Trying CAPTCHA...')
        #         holdings_url = f'https://nasdaqcsd.com/statistics/et/shareholders?security={stock.isin}&captcha[id]=' \
        #                        f'{captcha_id}&captcha[input]={captcha_input}'
        #         holdings_response = requests.get(holdings_url, cookies=dict(PHPSESSID=session_id))
        #         holdings_soup = bs4.BeautifulSoup(holdings_response.text, 'html.parser')
        #         try:
        #             # metadata_table = holdings_soup.select('table')[0]
        #             shareholders_table = holdings_soup.select('.most-numbers')[0]
        #             with open('last_result.txt', 'a') as f:
        #                 f.write(str(shareholders_table))
        #             print(shareholders_table)
        #             content_file = ContentFile(image_content)
        #             captcha = Captcha(
        #                 md5=captcha_id,
        #                 session_id=session_id,
        #                 answer=captcha_input
        #             )
        #             captcha.save()
        #             captcha.image.save(str(captcha.pk) + '.png', content_file, False)
        #             captcha.save()
        #             shareholders_retrieved = True
        #         except IndexError:
        #             continue
