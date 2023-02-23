from decimal import Decimal

from nuke import parse_nuke_command
from settings import LONG_LEVELS, SHORT_LEVELS, STOPS_SUM, NUKE_LEVELS
from tools.get_patch_prepare_data import (
    async_get_api_data,
    get_current_prices,
    prepare_asset_data,
    parse_ticker_info,
)


def sum_is_valid(asset, sum) -> bool:
    return sum > asset.price * asset.lot


async def process_long_stops_list(assets, levels, sum):
    orders = []
    for asset in assets:
        for discount in levels:
            stop_price = (
                (Decimal('100') - Decimal(discount)) * asset.price / 100
            )
            orders.append([asset, stop_price, int(sum / stop_price)])
    orders_placed = 0
    for order in orders:
        await order[0].place_long_stop(order[1], order[2])
        orders_placed += 1
    return (
        f'Stop placement complete. {orders_placed} stops placed.\n'
        f'Levels in %: {levels}, sum: {sum}'
    )


async def place_long_stops(*args, **kwargs):
    stops_assets = await async_get_api_data('stops')
    assets = get_current_prices(prepare_asset_data(stops_assets))
    return await process_long_stops_list(assets, LONG_LEVELS, STOPS_SUM)


async def place_short_stops(*args, **kwargs):
    shorts_assets = await async_get_api_data('shorts')
    assets = get_current_prices(prepare_asset_data(shorts_assets))
    orders = []
    for asset in assets:
        for discount in SHORT_LEVELS:
            stop_price = (
                (Decimal('100') + Decimal(discount)) * asset.price / 100
            )
            orders.append([asset, stop_price, int(STOPS_SUM / stop_price)])
    orders_placed = 0
    for order in orders:
        await order[0].place_short_stop(order[1], order[2])
        orders_placed += 1
    return (
        f'Short stops placement complete. {orders_placed} stops placed.\n'
        f'Levels in %: {SHORT_LEVELS}, sum: {STOPS_SUM}'
    )


async def process_nuke_command(command, *args, **kwargs):
    ticker, sum = parse_nuke_command(command)
    ticker_data = parse_ticker_info(ticker)
    assets = get_current_prices(prepare_asset_data([ticker_data]))
    asset = assets[0]
    stop_sum = sum // 4
    if not sum_is_valid(asset, stop_sum):
        return 'Sum is too small, cancelling Nuke command'
    return await process_long_stops_list(assets, NUKE_LEVELS, stop_sum)
