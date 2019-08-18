from django.db import models
from djmoney.models.fields import MoneyField

currency_choices = [('EUR', 'Euro')]


class Stock(models.Model):
    ticker = models.CharField(blank=False, null=False, max_length=5)
    name = models.CharField(blank=False, null=False, max_length=255)
    issuer = models.CharField(blank=False, null=False, max_length=255)
    total_issued = models.IntegerField(blank=False, null=False)
    registry_code = models.IntegerField(blank=False, null=False)
    isin = models.CharField(blank=False, null=False, max_length=12)
    nominal_share_price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', blank=True, null=True,
                                     currency_choices=currency_choices)
    latest_market_share_price = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', blank=True,
                                           null=True, currency_choices=currency_choices)
    nominal_market_cap = MoneyField(max_digits=20, decimal_places=2, default_currency='EUR', blank=True, null=True,
                                    currency_choices=currency_choices)
    latest_real_market_cap = MoneyField(max_digits=20, decimal_places=2, default_currency='EUR', blank=True, null=True,
                                        currency_choices=currency_choices)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker


class StockPosition(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    holder = models.CharField(blank=False, null=False, max_length=255)
    amount = models.IntegerField(blank=False, null=False)
    at_date = models.DateField(blank=False, null=False)
    is_insider = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.stock} - {self.holder} - {self.at_date} - {self.amount}'


# Keep these around to train own neural net once Google credit runs out: https://github.com/Kagami/chaptcha
class Captcha(models.Model):
    md5 = models.CharField(max_length=32, blank=False, null=False)
    session_id = models.CharField(max_length=35, blank=False, null=False)
    image = models.ImageField(upload_to='media/captchas/', blank=False, null=False)
    answer = models.CharField(max_length=4, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.pk} - {self.answer}'
