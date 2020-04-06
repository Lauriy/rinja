import datetime
import re

import bs4
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from google.cloud import vision
from google.cloud.vision import types

from rinja.models import Stock, Captcha, StockPosition, StockPositionNetChange, StockPositionChangeTypes


class Command(BaseCommand):
    help = 'Scrapes all stocks - intended to be run daily'

    def handle(self, *args, **options):
        all_supported_stocks = Stock.objects.all()
        captcha_retrieval_url = 'https://nasdaqcsd.com/statistics/en/shareholders'
        google_vision_client = vision.ImageAnnotatorClient()
        for stock in all_supported_stocks[:1]:
            # if stock.ticker == 'MRK1T':
            #     continue
            print(f'Trying stock {stock.ticker}')
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
                print('Trying CAPTCHA...')
                holdings_url = f'https://nasdaqcsd.com/statistics/en/shareholders?security={stock.isin}&captcha[id]=' \
                               f'{captcha_id}&captcha[input]={captcha_input}'
                holdings_response = requests.get(holdings_url, cookies=dict(PHPSESSID=session_id))
                holdings_soup = bs4.BeautifulSoup(holdings_response.text, 'html.parser')
                # print(holdings_soup)
                tables = holdings_soup.select('.table-striped')
                if not len(tables):
                    print(f'{len(tables)} is not enough tables')
                    continue
                # metadata_table = holdings_soup.select('table')[0]
                shareholders_table = holdings_soup.select('.most-numbers')[0]
                with open('last_result.txt', 'a') as f:
                    f.write(str(shareholders_table))
                # print(shareholders_table)
                content_file = ContentFile(image_content)
                captcha = Captcha(
                    md5=captcha_id,
                    session_id=session_id,
                    answer=captcha_input
                )
                captcha.save()
                captcha.image.save(str(captcha.answer) + '.png', content_file, False)
                captcha.save()
                shareholder_rows = holdings_soup.select('.most-numbers')[0].select('tbody')[0].select('tr')
                for shareholder_row in shareholder_rows:
                    shareholder_columns = shareholder_row.select('td')
                    name = shareholder_columns[0].decode_contents()
                    amount = int(
                        re.sub(r'\s+', '', shareholder_columns[1].decode_contents(), flags=re.UNICODE).replace(',',
                                                                                                               ''))
                    # Sadly we can only match by names...so 2 Jaan Tamms may inevitably happen to have the same amount
                    # of stocks on hand at the same moment...
                    # is_exact_existing_position = StockPosition.objects.filter(stock=stock, holder=name,
                    #                                                           amount=amount).exists()
                    existing_positions = StockPosition.objects.filter(stock=stock, holder=name).all()
                    exact_match_found = False
                    for position in existing_positions:
                        if position.amount == amount:
                            print(f'Exact matching position found for {amount} {stock} and {name}, skipping update.')
                            exact_match_found = True
                            position.checked = datetime.datetime.now()
                            position.save()
                    if exact_match_found:
                        continue
                    # TODO: DRY
                    if len(existing_positions) > 1:
                        print(f'Complex situation detected, these holdings are all a match:')
                        for position in existing_positions:
                            print(position)
                            position.checked = datetime.datetime.now()
                            position.save()
                        print('Updating the first one if need be')
                        if existing_positions[0].amount != amount:
                            existing_positions[0].amount = amount
                            existing_positions[0].save()
                            StockPositionNetChange(
                                stock_position=existing_positions[0],
                                type=StockPositionChangeTypes.BUY if amount > existing_positions[
                                    0].amount else StockPositionChangeTypes.SELL,
                                amount=abs(existing_positions[0].amount - amount)
                            ).save()
                    if len(existing_positions) == 0:
                        # TODO: Don't mark initial state as buys
                        print(f'Saving fresh position {amount} {stock} and {name}')
                        new_position = StockPosition(
                            stock=stock,
                            holder=name,
                            amount=amount,
                            checked=datetime.datetime.now()
                            # at_date=now - datetime.timedelta(days=settings.STOCK_HOLDING_REPORT_DELAY_DAYS)
                        )
                        new_position.save()
                        StockPositionNetChange(
                            stock_position=new_position,
                            type=StockPositionChangeTypes.BUY,
                            amount=amount
                        ).save()
                    if len(existing_positions) == 1:
                        print(f'Exactly one holding found')
                        if existing_positions[0].amount != amount:
                            existing_positions[0].amount = amount
                            StockPositionNetChange(
                                stock_position=existing_positions[0],
                                type=StockPositionChangeTypes.BUY if amount > existing_positions[
                                    0].amount else StockPositionChangeTypes.SELL,
                                amount=abs(existing_positions[0].amount - amount)
                            ).save()
                        existing_positions[0].checked = datetime.datetime.now()
                        existing_positions[0].save()
                shareholders_retrieved = True
# TODO: Delete all that didn't get checked - means they sold
