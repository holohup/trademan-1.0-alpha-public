from decimal import Decimal

from base.models import Figi, RestoreStops, SellBuy, Spread, Stops
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Figi
        fields = (
            'figi',
            'ticker',
            'min_price_increment',
            'lot',
            'morning_trading',
            'evening_trading',
            'asset_type'
        )
        read_only_fields = fields


class BasicDataSerializer(serializers.ModelSerializer):
    figi = serializers.CharField(source='asset.figi')
    min_price_increment = serializers.DecimalField(
        source='asset.min_price_increment', decimal_places=10, max_digits=20
    )
    ticker = serializers.CharField(source='asset.ticker')
    lot = serializers.IntegerField(source='asset.lot')

    class Meta:
        model = Stops
        fields = (
            'figi',
            'ticker',
            'min_price_increment',
            'lot',
        )
        read_only_fields = fields


class StopsSerializer(BasicDataSerializer):
    pass


class SellBuySerializer(BasicDataSerializer):
    asset_type = serializers.CharField(source='asset.asset_type')
    morning_trading = serializers.BooleanField(source='asset.morning_trading')
    evening_trading = serializers.BooleanField(source='asset.evening_trading')

    class Meta:
        model = SellBuy
        fields = (
            'id',
            'figi',
            'ticker',
            'min_price_increment',
            'lot',
            'sell',
            'amount',
            'executed',
            'avg_exec_price',
            'asset_type',
            'morning_trading',
            'evening_trading',
        )
        read_only_fields = (
            'id',
            'figi',
            'min_price_increment',
            'ticker',
            'lot',
            'sell',
            'amount',
            'asset_type',
            'morning_trading',
            'evening_trading'
        )

    def validate_executed(self, data):
        if data <= Decimal('0'):
            raise ValidationError('Executed must be > 0.')
        return super().validate(data)

    def validate_avg_exec_price(self, data):
        if data <= Decimal('0'):
            raise ValidationError('Avg_exec_price must be > 0.')
        return super().validate(data)


class RestoreStopsSerializer(BasicDataSerializer):
    class Meta:
        model = RestoreStops
        fields = (
            'id',
            'figi',
            'min_price_increment',
            'ticker',
            'lot',
            'sell',
            'amount',
            'price',
        )


class TickerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Figi
        fields = (
            'id',
            'min_price_increment',
            'figi',
            'ticker',
            'name',
            'lot',
            'asset_type',
            'api_trading_available',
            'short_enabled',
            'buy_enabled',
            'sell_enabled',
            'basic_asset_size',
        )


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
