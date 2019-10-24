from django.core.management.base import BaseCommand

from rinja.models import Stock, Captcha
from rinja.scraper import Scraper


class Command(BaseCommand):
    help = 'Scrapes and stores CATPCHAs for neural net training later on'

    def handle(self, *args, **options):
        stock = Stock.objects.filter(pk=18).first()
        scraper = Scraper()
        while True:
            captcha_id, captcha_input, session_id, content_file = scraper.retrieve_4_letter_captcha_candidate()
            holders_list = scraper.retrieve_holding_data_using_captcha(stock.isin, captcha_id, captcha_input,
                                                                       session_id)
            if holders_list:
                captcha = Captcha(
                    md5=captcha_id,
                    session_id=session_id,
                    answer=captcha_input
                )
                captcha.save()
                captcha.image.save(str(captcha.answer) + '.png', content_file, False)
                captcha.save()
                continue
