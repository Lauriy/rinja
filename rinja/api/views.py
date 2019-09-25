from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from rinja.api.serializers import StockScrapingResultSerializer
from rinja.scraper import retrieve_general_market_data


class AllStocksViewset(viewsets.ViewSet):
    serializer_class = StockScrapingResultSerializer

    def list(self, request: Request):
        # stocks = cache.get('cached_stocks', None)
        # if not stocks:
        stocks = retrieve_general_market_data()
            # cache.set('cached_stocks', stocks, settings.STOCKS_CACHE_TTL)
        serializer = self.serializer_class(instance=stocks, many=True)

        return Response(serializer.data)
