# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from api.models import Captcha, Stock

admin.site.register(Captcha)
admin.site.register(Stock)
