from django.contrib import admin

from .models import Figi, SellBuy, Spread, SpreadStats, StopOrder, Stops


@admin.register(SellBuy)
class SellBuyAdmin(admin.ModelAdmin):
    list_display = (
        'asset',
        'sell',
        'amount',
        'executed',
        'avg_exec_price',
        'active',
    )
    list_display_links = ('asset',)
    autocomplete_fields = ('asset',)
    list_editable = ('amount', 'sell', 'executed', 'active')
    list_filter = ('active',)


@admin.register(Stops)
class StopsAdmin(admin.ModelAdmin):
    list_display = ('asset', 'stop_blacklist', 'short_blacklist', 'whitelist')
    list_editable = ('stop_blacklist', 'short_blacklist', 'whitelist')
    list_filter = ('stop_blacklist', 'short_blacklist', 'whitelist')
    list_per_page = 200


@admin.register(Spread)
class SpreadAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'price',
        'sell',
        'amount',
        'ratio',
        'executed',
        'avg_exec_price',
        'active',
    )
    list_display_links = ('__str__',)
    autocomplete_fields = ('near_leg', 'far_leg')
    list_editable = (
        'amount',
        'sell',
        'price',
        'active',
    )
    list_filter = ('active',)

    fields = (
        'far_leg',
        'near_leg',
        'active',
        'sell',
        'price',
        'amount',
        'editable_ratio',
        'spread_stats',
    )
    readonly_fields = ('spread_stats',)

    def spread_stats(self, obj):
        return (
            f'Far leg executed: {obj.stats.far_leg_executed} for '
            f'{float(obj.stats.far_leg_avg_price)}, near leg executed: '
            f'{obj.stats.near_leg_executed} for '
            f'{float(obj.stats.near_leg_avg_price)}'
            f' Avg price = {float(obj.avg_exec_price)}'
        )

    def save_model(self, request, obj: Spread, form, change):
        if not obj.pk:
            obj.stats = SpreadStats.objects.create()
        obj.save()


@admin.register(StopOrder)
class StopOrderAdmin(admin.ModelAdmin):
    list_display = (
        'asset',
        'price',
        'stop_price',
        'sell',
        'lots',
        'active',
        'order_type',
    )
    list_display_links = ('asset',)
    autocomplete_fields = ('asset',)
    list_editable = (
        'price',
        'stop_price',
        'lots',
        'sell',
        'active',
        'order_type',
    )
    list_filter = ('active', 'order_type', 'sell')
    fields = (
        'asset',
        'price',
        'stop_price',
        'sell',
        'lots',
        'active',
        'order_type',
    )


@admin.register(Figi)
class FigiAdmin(admin.ModelAdmin):
    list_display = (
        'ticker',
        'lot',
        'min_price_increment',
        'asset_type',
        'api_trading_available',
        'short_enabled',
        'buy_enabled',
        'sell_enabled',
        'basic_asset',
        'basic_asset_size',
        'morning_trading',
        'evening_trading',
    )
    list_filter = ('asset_type', 'morning_trading', 'evening_trading')
    search_fields = ('ticker', 'figi', 'name')
    list_max_show_all = 5000
    list_per_page = 200
