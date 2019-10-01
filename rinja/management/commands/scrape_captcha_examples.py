import bs4
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from google.cloud import vision
from google.cloud.vision import types

from rinja.models import Stock, Captcha


class Command(BaseCommand):
    help = 'Scrapes and stores CATPCHAs for neural net training later on'

    def handle(self, *args, **options):
        all_supported_stocks = Stock.objects.all()
        captcha_retrieval_url = 'https://nasdaqcsd.com/statistics/en/shareholders'
        google_vision_client = vision.ImageAnnotatorClient()
        stock = all_supported_stocks[0]
        while True:
        #for stock in all_supported_stocks[:1]:
            shareholders_retrieved = False
            while shareholders_retrieved is False:
                captcha_input = None
                while not captcha_input or len(captcha_input) != 4:
                    print('Trying to retrieve 4-letter CAPTCHA answer...')
                    captcha_page = requests.get(captcha_retrieval_url)
                    session_id = captcha_page.cookies['PHPSESSID']
                    soup = bs4.BeautifulSoup(captcha_page.text, 'html.parser')
                    captcha_id = soup.select('#captcha-id')[0]['value']
                    captcha_image_url = f'https://nasdaqcsd.com/statistics/graphics/captcha/{captcha_id}.png'
                    image_content = requests.get(captcha_image_url).content
                    image_to_run_vision_on = types.Image(content=image_content)
                    vision_response = google_vision_client.text_detection(image=image_to_run_vision_on)
                    try:
                        captcha_input = vision_response.text_annotations[0].description.strip()
                    except IndexError:
                        continue
                print(f'Trying CAPTCHA with answer {captcha_input} on stock {stock.ticker} with session ID {session_id}')
                holdings_url = f'https://nasdaqcsd.com/statistics/et/shareholders?security={stock.isin}&captcha[id]=' \
                               f'{captcha_id}&captcha[input]={captcha_input}'
                holdings_response = requests.get(holdings_url, cookies=dict(PHPSESSID=session_id))
                holdings_soup = bs4.BeautifulSoup(holdings_response.text, 'html.parser')
                #try:
                # metadata_table = holdings_soup.select('table')[0]
                tables = holdings_soup.select('.table-striped')
                if not len(tables):
                    print(f'{len(tables)} is not enough tables')
                    continue
                # with open('last_result.txt', 'a') as f:
                #     f.write(str(shareholders_table))
                # print(shareholders_table)
                content_file = ContentFile(image_content)
                captcha = Captcha(
                    md5=captcha_id,
                    session_id=session_id,
                    answer=captcha_input
                )
                captcha.save()
                captcha.image.save(str(captcha.pk) + '.png', content_file, False)
                captcha.save()
                shareholders_retrieved = True
                # except IndexError:
                #     continue
