# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models


def get_captchas_date_based_path(instance, filename):
    return '/'.join([
        'captchas',
        instance.created_at.year,
        instance.created_at.month,
        instance.created_at.day,
        '-'.join([
            instance.answer if instance.answer else '',
            instance.md5
        ]) + '.' + filename.split('.')[-1]
    ])


class Captcha(models.Model):
    # Saving these to train a neural net later: https://github.com/Kagami/chaptcha
    image = models.ImageField(upload_to=get_captchas_date_based_path, blank=False, null=False)
    md5 = models.CharField(max_length=32, blank=True, null=False)
    answer = models.CharField(max_length=4, blank=False, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
