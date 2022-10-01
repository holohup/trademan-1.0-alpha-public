from rest_framework import serializers

from base.models import Stops, SellBuy, RestoreStops, Spread


class BasicDataSerializer(serializers.ModelSerializer):
    figi = serializers.SerializerMethodField()
    increment = serializers.SerializerMethodField()
    lot = serializers.SerializerMethodField()
    ticker = serializers.SerializerMethodField()

    class Meta:
        model = Stops
        fields = ('figi', 'ticker', 'increment', 'lot', )

    def get_figi(self, obj):
        return obj.asset.figi

    def get_increment(self, obj):
        return obj.asset.min_price_increment

    def get_ticker(self, obj):
        return obj.asset.ticker

    def get_lot(self, obj):
        return obj.asset.lot


class StopsSerializer(BasicDataSerializer):
    pass


class SellBuySerializer(BasicDataSerializer):

    class Meta:
        model = SellBuy
        fields = ('id', 'figi', 'ticker', 'increment', 'lot', 'sell', 'amount', 'executed')
        read_only_fields = ('id', 'figi', 'increment', 'ticker', 'lot', 'sell', 'amount',)


class SpreadsSerializer(BasicDataSerializer):
    near_leg_figi = serializers.SerializerMethodField()
    near_leg_increment = serializers.SerializerMethodField()
    near_leg_lot = serializers.SerializerMethodField()
    near_leg_ticker = serializers.SerializerMethodField()

    class Meta:
        model = Spread
        fields = (
            'id',
            'figi', 'ticker', 'increment', 'lot',
            'near_leg_figi', 'near_leg_ticker', 'near_leg_increment', 'near_leg_lot',
            'sell', 'price', 'amount', 'executed'
        )
        read_only_fields = (
            'id',
            'figi', 'ticker', 'increment', 'lot',
            'near_leg_figi', 'near_leg_ticker', 'near_leg_increment', 'near_leg_lot',
            'sell', 'price', 'amount'
        )
    def get_near_leg_figi(self, obj):
        return obj.near_leg.figi

    def get_near_leg_increment(self, obj):
        return obj.near_leg.min_price_increment

    def get_near_leg_ticker(self, obj):
        return obj.near_leg.ticker

    def get_near_leg_lot(self, obj):
        return obj.near_leg.lot

class RestoreStopsSerializer(BasicDataSerializer):

    class Meta:
        model = RestoreStops
        fields = ('id', 'figi', 'increment', 'ticker', 'lot', 'sell', 'amount', 'price')