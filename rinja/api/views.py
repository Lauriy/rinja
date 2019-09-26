from django.conf import settings
from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response

from rinja.api.serializers import StockScrapingResultSerializer
from rinja.forms import ApiStocksListingRequestSchema
from rinja.models import WatchlistEntry
from rinja.scraper import retrieve_general_market_data


class AllStocksViewset(viewsets.ViewSet):
    serializer_class = StockScrapingResultSerializer

    def list(self, request: Request) -> Response:
        form = ApiStocksListingRequestSchema(request.GET)
        is_watchlist = False
        if form.is_valid():
            is_watchlist = form.cleaned_data['watchlist']
        stocks = cache.get('cached_stocks', None)
        if not stocks:
            stocks = retrieve_general_market_data()
            cache.set('cached_stocks', stocks, settings.STOCKS_CACHE_TTL)
        if is_watchlist:
            if not request.user:
                raise AuthenticationFailed
            flat_watchlist_tickers = WatchlistEntry.objects.filter(user=request.user).values_list('ticker', flat=True)
            stocks = [stock for stock in stocks if stock['ticker'] in flat_watchlist_tickers]
        serializer = self.serializer_class(instance=stocks, many=True)

        return Response(serializer.data)


class SubscriptionViewset(viewsets.ViewSet):
    def update(self, request, pk):
        print(pk)
