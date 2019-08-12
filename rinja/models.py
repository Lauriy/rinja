from django.db import models
from djmoney.models.fields import MoneyField


class Stock(models.Model):
    name = models.CharField(blank=False, null=False, max_length=255)
    issuer = models.CharField(blank=False, null=False, max_length=255)
    total_issued = models.IntegerField(blank=False, null=False)
    registry_code = models.IntegerField(blank=False, null=False)
    isin = models.CharField(blank=False, null=False, max_length=12)
    nominal_value = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, null=True, blank=True)


class Captcha(models.Model):
    md5 = models.CharField(max_length=32, blank=True, null=False)
    image = models.ImageField(upload_to='captchas/', blank=False, null=False)
    answer = models.CharField(max_length=4, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
