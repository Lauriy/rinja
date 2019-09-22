from django.http import HttpResponse
from django.template import loader


def all_stocks(request):
    template = loader.get_template('stocks.html')
    context = {

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
