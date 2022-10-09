from django.contrib import admin
from .models import Figi, SellBuy, Spread, RestoreStops, Stops, Bonds


@admin.register(SellBuy)
class SellBuyAdmin(admin.ModelAdmin):
    list_display = ('asset', 'sell', 'amount', 'executed', 'active')
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
    list_display = ('asset', 'near_leg', 'price', 'sell', 'amount', 'executed', 'active')
    list_display_links = ('near_leg', 'asset')
    autocomplete_fields = ('near_leg', 'asset')
    list_editable = ('amount', 'sell', 'executed', 'price', 'active')
    list_filter = ('active',)


@admin.register(RestoreStops)
class RestoreStopsAdmin(admin.ModelAdmin):
    list_display = ('asset', 'price', 'sell', 'amount', 'active')
    list_display_links = ('asset',)
    autocomplete_fields = ('asset',)
    list_editable = ('amount', 'price', 'active')
    list_filter = ('active',)


@admin.register(Figi)
class FigiAdmin(admin.ModelAdmin):
    list_display = (
        'ticker', 'lot', 'min_price_increment', 'figi', 'name',
        'type', 'api_trading_available', 'short_enabled', 'buy_enabled',
        'sell_enabled', 'basic_asset_size'
    )
    list_filter = ('type',)
    search_fields = ('ticker', 'figi', 'name')
    list_max_show_all = 5000
    list_per_page = 200

@admin.register(Bonds)
class BondsAdmin(admin.ModelAdmin):
    list_display = ('asset', 'whitelist')
    list_editable = ('whitelist',)
    list_filter = ('whitelist',)
    list_per_page = 100
    autocomplete_fields = ('asset',)
