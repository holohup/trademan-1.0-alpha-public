from decimal import Decimal

from base.models import Figi, RestoreStops, SellBuy, Spread, Stops
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
    increment = serializers.CharField(source='min_price_increment')

    class Meta:
        model = Figi
        fields = (
            'id',
            'increment',
            'figi',
            'ticker',
            'name',
            'lot',
            'type',
            'api_trading_available',
            'short_enabled',
            'buy_enabled',
            'sell_enabled',
            'basic_asset_size',
        )


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Figi
        fields = (
            'figi',
            'ticker',
            'min_price_increment',
            'lot',
        )
        read_only_fields = fields


class SpreadsSerializer(serializers.ModelSerializer):
    far_leg = AssetSerializer()
    near_leg = AssetSerializer()

    class Meta:
        model = Spread
        fields = (
            'id',
            'sell',
            'price',
            'amount',
            'ratio',
            'far_leg',
            'near_leg',
        )
        read_only_fields = (
            'id',
            'sell',
            'price',
            'amount',
            'ratio',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['far_leg']['executed'] = instance.stats.far_leg_executed
        data['near_leg']['executed'] = instance.stats.near_leg_executed
        data['far_leg']['avg_exec_price'] = str(
            instance.stats.far_leg_avg_price
        )
        data['near_leg']['avg_exec_price'] = str(
            instance.stats.near_leg_avg_price
        )
        return data

    def update(self, instance, validated_data):
        data = self.context.get('request').data
        instance.stats.far_leg_executed = data['far_leg']['executed']
        instance.stats.near_leg_executed = data['near_leg']['executed']
        instance.stats.far_leg_avg_price = Decimal(
            data['far_leg']['avg_exec_price']
        )
        instance.stats.near_leg_avg_price = Decimal(
            data['near_leg']['avg_exec_price']
        )
        instance.active = not data['far_leg']['executed'] >= instance.amount
        instance.stats.save()
        instance.save()
        return instance
