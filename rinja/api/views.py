import datetime

from rest_framework import viewsets
from rest_framework.response import Response

from rinja.api.serializers import StockScrapingResultSerializer
from rinja.scraper import retrieve_general_market_data_for_date, scrape_general_market_data_for_date


class AllStocksViewset(viewsets.ViewSet):
    serializer_class = StockScrapingResultSerializer

    def list(self, request):
        now = datetime.datetime.now()
        stocks = retrieve_general_market_data_for_date(now.year, now.month, now.day)
        serializer = self.serializer_class(instance=stocks, many=True)

        return Response(serializer.data)
