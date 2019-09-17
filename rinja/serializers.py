from rest_framework import serializers

from rinja.models import StockScrapingResult


class StockScrapingResultSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    ticker = serializers.CharField(max_length=5, source='Ticker')

    def create(self, validated_data):
        return StockScrapingResult(id=None, **validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        return instance
