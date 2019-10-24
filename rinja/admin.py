from django.contrib import admin

from rinja.models import Stock, Captcha, StockPosition

admin.site.register(Stock)
admin.site.register(Captcha)
admin.site.register(StockPosition)
