from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import serializers

from rinja.models import StockScrapingResult


class StockScrapingResultSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, max_length=5, source='Ticker')
    ticker = serializers.CharField(max_length=5, source='Ticker')
    name = serializers.CharField(max_length=100, source='Name')
    last_price = MoneyField(max_digits=10, decimal_places=3, default_currency='EUR', source='Last Price',
                            allow_null=True)
    change_percentage = serializers.DecimalField(max_digits=10, decimal_places=2, source='Price Change(%)',
                                                 allow_null=True)
    volume_eur = MoneyField(max_digits=10, decimal_places=3, default_currency='EUR', source='Turnover',
                            allow_null=True)
    bid = MoneyField(max_digits=10, decimal_places=3, default_currency='EUR', source='Best bid',
                     allow_null=True)
    ask = MoneyField(max_digits=10, decimal_places=3, default_currency='EUR', source='Best ask',
                     allow_null=True)
    open_price = MoneyField(max_digits=10, decimal_places=3, default_currency='EUR', source='Open Price',
                            allow_null=True)
    last_close_price = MoneyField(max_digits=10, decimal_places=3, default_currency='EUR', source='Last close Price',
                                  allow_null=True)
    high_price = MoneyField(max_digits=10, decimal_places=3, default_currency='EUR', source='High Price',
                            allow_null=True)
    low_price = MoneyField(max_digits=10, decimal_places=3, default_currency='EUR', source='Low Price',
                           allow_null=True)
    average_price = MoneyField(max_digits=10, decimal_places=8, default_currency='EUR', source='Average Price',
                               allow_null=True)
    trades = serializers.IntegerField(source='Trades', allow_null=True)
    volume_self = serializers.IntegerField(source='Volume', allow_null=True)
    isin = serializers.CharField(max_length=12, source='ISIN')
    market = serializers.CharField(max_length=3, source='MarketPlace')
    segment = serializers.CharField(max_length=100, source='List/segment')
    currency = serializers.CharField(max_length=3, source='Currency')

    def create(self, validated_data):
        return StockScrapingResult(id=None, **validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        return instance
