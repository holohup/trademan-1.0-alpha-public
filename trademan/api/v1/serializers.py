from rest_framework import serializers

from base.models import Stops


class StopsSerializer(serializers.ModelSerializer):
    figi = serializers.SerializerMethodField()
    increment = serializers.SerializerMethodField()
    lot = serializers.SerializerMethodField()
    ticker = serializers.SerializerMethodField()

    class Meta:
        model = Stops
        fields = ('figi', 'increment', 'ticker', 'lot')

    def get_figi(self, obj):
        return obj.stock.figi

    def get_increment(self, obj):
        return obj.stock.min_price_increment

    def get_ticker(self, obj):
        return obj.stock.ticker

    def get_lot(self, obj):
        return obj.stock.lot
