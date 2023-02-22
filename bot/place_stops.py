from decimal import Decimal

from settings import LONG_LEVELS, SHORT_LEVELS, STOPS_SUM
from tools.get_patch_prepare_data import (
    async_get_api_data,
    get_current_prices,
    prepare_asset_data,
)


def price_is_valid(price):
    return price > 0


async def place_long_stops():
    stops_assets = await async_get_api_data('stops')
    assets = get_current_prices(prepare_asset_data(stops_assets))
    orders = []
    for asset in assets:
        if price_is_valid(asset.price):
            for discount in LONG_LEVELS:
                stop_price = (
                    (Decimal('100') - Decimal(discount)) * asset.price / 100
                )
                orders.append([asset, stop_price, int(STOPS_SUM / stop_price)])
        else:
            raise ValueError(f'Price is <=0! {asset}, {asset.price}')
    orders_placed = 0
    for order in orders:
        await order[0].place_long_stop(order[1], order[2])
        orders_placed += 1
    return (
        f'Stop placement complete. {orders_placed} stops placed.\n'
        f'Levels in %: {LONG_LEVELS}, sum: {STOPS_SUM}'
    )


async def place_short_stops():
    shorts_assets = await async_get_api_data('shorts')
    assets = get_current_prices(prepare_asset_data(shorts_assets))
    orders = []
    for asset in assets:
        if price_is_valid(asset.price):
            for discount in SHORT_LEVELS:
                stop_price = (
                    (Decimal('100') + Decimal(discount)) * asset.price / 100
                )
                orders.append([asset, stop_price, int(STOPS_SUM / stop_price)])
        else:
            raise ValueError(f'Price is <=0! {asset}, {asset.price}')
    orders_placed = 0
    for order in orders:
        await order[0].place_short_stop(order[1], order[2])
        orders_placed += 1
    return (
        f'Short stops placement complete. {orders_placed} stops placed.\n'
        f'Levels in %: {SHORT_LEVELS}, sum: {STOPS_SUM}'
    )
