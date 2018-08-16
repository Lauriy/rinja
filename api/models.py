# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from djmoney.models.fields import MoneyField


def get_captchas_date_based_path(instance, filename):
    return '/'.join([
        'media/uploads/captchas',
        str(instance.created_at.year),
        str(instance.created_at.month),
        str(instance.created_at.day),
        '-'.join(filter(None, [
            instance.answer if instance.answer else None,
            instance.md5
        ])) + '.' + filename.split('.')[-1]
    ])


class Captcha(models.Model):
    # Saving these to train a neural net later: https://github.com/Kagami/chaptcha
    image = models.ImageField(upload_to=get_captchas_date_based_path, blank=False, null=True)
    md5 = models.CharField(max_length=32, blank=False, null=False)
    answer = models.CharField(max_length=4, blank=True, null=True)
    session_id = models.CharField(max_length=32, blank=False, null=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Stock(models.Model):
    issuer = models.CharField(blank=False, null=False, max_length=255)
    registry_code = models.IntegerField(blank=False, null=False)
    name = models.CharField(blank=False, null=False, max_length=255)
    isin = models.CharField(blank=False, null=False, max_length=255)
    total_issued = models.IntegerField(blank=False, null=False)
    nominal_value = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR', blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name