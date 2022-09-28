from django.contrib import admin
from .models import Figi, SellBuy, Spread, RestoreStops


@admin.register(SellBuy)
class SellBuyAdmin(admin.ModelAdmin):
    list_display = ('asset', 'sell', 'amount', 'executed', 'active')
    list_display_links = ('asset',)
    autocomplete_fields = ('asset',)
    list_editable = ('amount', 'executed', 'active')
    list_filter = ('active',)


@admin.register(Spread)
class SpreadAdmin(admin.ModelAdmin):
    list_display = ('near_leg', 'asset', 'price', 'sell', 'amount', 'executed', 'active')
    list_display_links = ('near_leg', 'asset')
    autocomplete_fields = ('near_leg', 'asset')
    list_editable = ('amount', 'executed', 'price', 'active')
    list_filter = ('active',)


@admin.register(RestoreStops)
class RestoreStopsAdmin(admin.ModelAdmin):
    list_display = ('asset', 'price', 'sell', 'amount', 'executed', 'active')
    list_display_links = ('asset',)
    autocomplete_fields = ('asset',)
    list_editable = ('amount', 'executed', 'price', 'active')
    list_filter = ('active',)


@admin.register(Figi)
class FigiAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'lot', 'min_price_increment', 'figi', 'name', 'type')
    list_filter = ('type',)
    search_fields = ('ticker', 'figi', 'name')
    list_max_show_all = 5000
    list_per_page = 200


