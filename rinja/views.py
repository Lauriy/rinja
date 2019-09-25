from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.views.generic import UpdateView


def all_stocks(request):
    template = loader.get_template('stocks.html')
    context = {

    }

    return HttpResponse(template.render(context, request))


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = 'profile_edit.html'
    model = User
    fields = []

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('account_profile')

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
