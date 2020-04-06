from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from rinja.api.serializers import StockScrapingResultSerializer, WatchlistEntrySerializer
from rinja.forms import ApiStocksListingRequestSchema
from rinja.models import WatchlistEntry
from rinja.scraper import Scraper


class AllStocksViewset(viewsets.ViewSet):
    serializer_class = StockScrapingResultSerializer

    def list(self, request: Request) -> Response:
        form = ApiStocksListingRequestSchema(request.GET)
        is_watchlist = False
        if form.is_valid():
            is_watchlist = form.cleaned_data['watchlist']
        stocks = cache.get('cached_stocks', None)
        if not stocks:
            scraper = Scraper()
            stocks = scraper.retrieve_general_market_data()
            cache.set('cached_stocks', stocks, settings.STOCKS_CACHE_TTL)
        if is_watchlist:
            if not request.user:
                raise AuthenticationFailed
            flat_watchlist_tickers = WatchlistEntry.objects.filter(user_id=request.user.id).values_list('ticker', flat=True)
            stocks = [stock for stock in stocks if stock['Ticker'] in flat_watchlist_tickers]
        serializer = self.serializer_class(instance=stocks, many=True)

        return Response(serializer.data)


class WatchlistViewset(viewsets.ModelViewSet):
    serializer_class = WatchlistEntrySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']
    lookup_field = 'ticker'

    def get_queryset(self) -> QuerySet:
        return WatchlistEntry.objects.filter(user=self.request.user).all()

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        ticker = kwargs.get('ticker', None)
        response_content = None
        if ticker:
            existing_watchlist_entry = WatchlistEntry.objects.filter(ticker=ticker).first()
            if not existing_watchlist_entry:
                new_watchlist_entry = WatchlistEntry(
                    user=request.user,
                    ticker=ticker
                )
                new_watchlist_entry.save()
                serializer = self.get_serializer(new_watchlist_entry)
                response_content = serializer.data
                status = 200
            else:
                existing_watchlist_entry.delete()
                status = 204
        else:
            status = 400

        return Response(response_content, status=status)
