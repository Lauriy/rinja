from django.db import models
from djmoney.models.fields import MoneyField


# class Stock(models.Model):
#     name = models.CharField(blank=False, null=False)
#     issuer = models.CharField(blank=False, null=False)
#     total_issued = models.IntegerField(blank=False, null=False)
#     registry_code = models.IntegerField(blank=False, null=False)
#     isin = models.CharField(blank=False, null=False)
#     created = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)
#
#
# class StockQuote(models.Model):
#     stock = models.ForeignKey(Stock, related_name='quotes', blank=False, null=False)
#     value = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', blank=False, null=False)
#     time = models.DateTimeField(blank=False, null=False)
#     created = models.DateTimeField(auto_now_add=True)
#     modified = models.DateTimeField(auto_now=True)
#
#

class Captcha(models.Model):
    md5 = models.CharField(max_length=32, blank=True, null=False)
    image = models.ImageField(upload_to='captchas/', blank=False, null=False)
    answer = models.CharField(max_length=4, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)