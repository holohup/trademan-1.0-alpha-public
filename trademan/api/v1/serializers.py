from base.models import RestoreStops, SellBuy, Spread, Stops, Figi
from rest_framework import serializers


class BasicDataSerializer(serializers.ModelSerializer):
    figi = serializers.CharField(source='asset.figi')
    increment = serializers.DecimalField(
        source='asset.min_price_increment', decimal_places=10, max_digits=20
    )
    ticker = serializers.CharField(source='asset.ticker')
    lot = serializers.IntegerField(source='asset.lot')

    class Meta:
        model = Stops
        fields = (
            'figi',
            'ticker',
            'increment',
            'lot',
        )
        read_only_fields = fields


class StopsSerializer(BasicDataSerializer):
    pass


class SellBuySerializer(BasicDataSerializer):
    class Meta:
        model = SellBuy
        fields = (
            'id',
            'figi',
            'ticker',
            'increment',
            'lot',
            'sell',
            'amount',
            'executed',
        )
        read_only_fields = (
            'id',
            'figi',
            'increment',
            'ticker',
            'lot',
            'sell',
            'amount',
        )


class SpreadsSerializer(BasicDataSerializer):
    near_leg_figi = serializers.CharField(source='near_leg.figi')
    near_leg_increment = serializers.DecimalField(
        source='near_leg.min_price_increment', decimal_places=10, max_digits=20
    )
    near_leg_lot = serializers.IntegerField(source='near_leg.lot')
    near_leg_ticker = serializers.CharField(source='near_leg.ticker')
    near_leg_type = serializers.CharField(source='near_leg.type')
    base_asset_amount = serializers.IntegerField(
        source='asset.basic_asset_size'
    )

    class Meta:
        model = Spread
        fields = (
            'id',
            'figi',
            'ticker',
            'increment',
            'lot',
            'near_leg_figi',
            'near_leg_ticker',
            'near_leg_increment',
            'near_leg_lot',
            'sell',
            'price',
            'amount',
            'executed',
            'exec_price',
            'near_leg_type',
            'base_asset_amount',
        )
        read_only_fields = (
            'id',
            'figi',
            'ticker',
            'increment',
            'lot',
            'near_leg_figi',
            'near_leg_ticker',
            'near_leg_increment',
            'near_leg_lot',
            'sell',
            'price',
            'amount',
            'near_leg_type',
            'base_asset_amount',
        )


class RestoreStopsSerializer(BasicDataSerializer):
    class Meta:
        model = RestoreStops
        fields = (
            'id',
            'figi',
            'increment',
            'ticker',
            'lot',
            'sell',
            'amount',
            'price',
        )


class TickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Figi
        fields = '__all__'
