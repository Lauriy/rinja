import datetime

from django.http import HttpResponse
from django.template import loader
from rest_framework import viewsets
from rest_framework.response import Response

from rinja.scraper import retrieve_general_market_data_for_date
from rinja.serializers import StockScrapingResultSerializer


class AllStocksViewset(viewsets.ViewSet):
    serializer_class= StockScrapingResultSerializer

    def list(self, request):
        now = datetime.datetime.now()
        stocks = retrieve_general_market_data_for_date(now.year, now.month, now.day)
        serializer = self.serializer_class(instance=stocks, many=True)

        return Response(serializer.data)

def all_stocks(request):
    template = loader.get_template('stocks.html')
    now = datetime.datetime.now()
    stocks = retrieve_general_market_data_for_date(now.year, now.month, now.day)
    for stock in stocks:
        stock['Segment'] = stock['List/segment']
        del stock['List/segment']
    context = {
        'stocks': stocks
    }

    return HttpResponse(template.render(context, request))

# def all_stocks(request):
#     template = loader.get_template('stocks.html')
#     stocks = Stock.objects.order_by('ticker')
#     for stock in stocks:
#         if stock.nominal_market_cap and stock.latest_real_market_cap:
#             stock.mcap_ratio = round(stock.latest_real_market_cap / stock.nominal_market_cap, 2)
#     context = {
#         'stocks': stocks
#     }
#
#     return HttpResponse(template.render(context, request))
