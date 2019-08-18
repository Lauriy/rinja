import decimal

import bs4
import requests
from django.core.management.base import BaseCommand

from rinja.models import Stock


class Command(BaseCommand):
    help = 'Scrapes OMXT stock prices - intended to be run hourly when market is open'

    def handle(self, *args, **options):
        all_supported_stocks = Stock.objects.all()
        url = 'https://www.nasdaqbaltic.com/market/?pg=mainlist'
        prices_response = requests.get(url)
        tables = bs4.BeautifulSoup(prices_response.text, 'html.parser').select('table')
        main_list = tables[1]
        secondary_list = tables[2]
        first_north_list = tables[4]
        # FIXME: DRY
        for row in main_list.select('tbody > tr'):
            isin = row.get('id').replace('eq-', '').strip()
            try:
                price = decimal.Decimal(row.select('td')[4].decode_contents().strip())
            except decimal.InvalidOperation:
                continue
            stock_to_update: Stock = all_supported_stocks.filter(isin=isin).first()
            if stock_to_update:
                stock_to_update.latest_market_share_price = price
                stock_to_update.latest_real_market_cap = price * stock_to_update.total_issued
                stock_to_update.save()
        for row in secondary_list.select('tbody > tr')[:1]:
            isin = row.get('id').replace('eq-', '').strip()
            try:
                price = decimal.Decimal(row.select('td')[4].decode_contents().strip())
            except decimal.InvalidOperation:
                continue
            stock_to_update: Stock = all_supported_stocks.filter(isin=isin).first()
            if stock_to_update:
                stock_to_update.latest_market_share_price = price
                stock_to_update.latest_real_market_cap = price * stock_to_update.total_issued
                stock_to_update.save()
        for row in first_north_list.select('tbody > tr'):
            isin = row.get('id').replace('eq-', '').strip()
            try:
                price = decimal.Decimal(row.select('td')[4].decode_contents().strip())
            except decimal.InvalidOperation:
                continue
            stock_to_update: Stock = all_supported_stocks.filter(isin=isin).first()
            if stock_to_update:
                stock_to_update.latest_market_share_price = price
                stock_to_update.latest_real_market_cap = price * stock_to_update.total_issued
                stock_to_update.save()
