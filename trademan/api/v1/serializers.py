from decimal import Decimal

from base.models import Figi, SellBuy, Spread, SpreadStats, Stops
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
            'min_price_increment',
            'ticker',
            'figi',
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
    far_leg = AssetSerializer(read_only=True)
    near_leg = AssetSerializer(read_only=True)
    far_leg_figi = serializers.CharField(write_only=True)
    near_leg_figi = serializers.CharField(write_only=True)

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
            'far_leg_figi',
            'near_leg_figi',
            'editable_ratio',
        )
        read_only_fields = (
            'id',
            'ratio',
            'far_leg',
            'near_leg',
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

    def create(self, validated_data):
        """
        Create a new spread with associated SpreadStats.
        
        The spread is created with active=True by default (model default).
        A SpreadStats object is automatically created and associated.
        """
        # Extract FIGI data for creation
        far_leg_figi = validated_data.pop('far_leg_figi')
        near_leg_figi = validated_data.pop('near_leg_figi')
        
        # Get the Figi objects
        try:
            far_leg = Figi.objects.get(figi=far_leg_figi)
            near_leg = Figi.objects.get(figi=near_leg_figi)
        except Figi.DoesNotExist as e:
            raise ValidationError(f"Invalid FIGI: {str(e)}")
        
        # Create SpreadStats object
        stats = SpreadStats.objects.create()
        
        # Create the spread
        spread = Spread.objects.create(
            far_leg=far_leg,
            near_leg=near_leg,
            stats=stats,
            **validated_data
        )
        
        return spread

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
