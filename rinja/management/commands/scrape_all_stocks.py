import bs4
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from rinja.models import Stock, Captcha
from google.cloud import vision
from google.cloud.vision import types

class Command(BaseCommand):
    help = 'Scrapes all stocks - intended to be run daily'

    def handle(self, *args, **options):
        all_supported_stocks = Stock.objects.all()
        for stock in all_supported_stocks:
            captcha_retrieval_url = 'https://nasdaqcsd.com/statistics/et/shareholders'
            captcha_page = requests.get(captcha_retrieval_url)
            session_id = captcha_page.cookies['PHPSESSID']
            print(session_id)
            soup = bs4.BeautifulSoup(captcha_page.text, 'html.parser')
            captcha_id = soup.select('#captcha-id')[0]['value']
            print(captcha_id)
            captcha_image_url = f'https://nasdaqcsd.com/statistics/graphics/captcha/{captcha_id}.png'
            image_content = requests.get(captcha_image_url).content
            content_file = ContentFile(image_content)
            # instance = Captcha(
            #     md5=captcha_id,
            #     session_id=session_id
            # )
            # instance.save()
            # instance.image.save(str(instance.pk) + '.png', image_content, False)
            # instance.save()
            google_vision_client = vision.ImageAnnotatorClient()
            image_to_run_vision_on = types.Image(content=image_content)
            vision_response = google_vision_client.text_detection(image=image_to_run_vision_on)
            print(vision_response)
            labels = vision_response.text_annotations
            print('Labels:')
            for label in labels:
                print(label.description)
            # url = f'https://nasdaqcsd.com/statistics/et/shareholders?security={stock.isin}&captcha[id]={captcha_id}&captcha[input]={captcha_input}'
