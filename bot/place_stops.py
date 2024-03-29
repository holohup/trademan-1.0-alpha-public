from decimal import Decimal

from settings import LONG_LEVELS, NUKE_LEVELS, SHORT_LEVELS, STOPS_SUM
from tools.classes import StopOrder, StopOrderParams
from tools.get_patch_prepare_data import (async_get_api_data,
                                          get_current_prices,
                                          parse_ticker_info,
                                          prepare_asset_data)
from tools.orders import place_stop_order
from tools.utils import parse_ticker_int_args

LONG_STOP_PARAMS = StopOrderParams('buy', 'take_profit', 'gtd')
SHORT_STOP_PARAMS = StopOrderParams('sell', 'take_profit', 'gtd')
LEVELS = {
    'stops': LONG_LEVELS,
    'shorts': [str(-int(level)) for level in SHORT_LEVELS],
}
PARAMS = {'stops': LONG_STOP_PARAMS, 'shorts': SHORT_STOP_PARAMS}


def sum_is_valid(asset, sum) -> bool:
    return sum > asset.price * asset.lot


async def process_stops(assets, levels, sum, params):
    orders = []
    for asset in assets:
        for discount in levels:
            stop_price = (
                (Decimal('100') - Decimal(discount)) * asset.price / 100
            )
            orders.append(StopOrder(asset, stop_price, sum, params))
    orders_placed = 0
    for order in orders:
        await place_stop_order(order)
        orders_placed += 1
    return (
        f'Stop placement complete. {orders_placed} stops placed.\n'
        f'Levels in %: {levels}, sum: {sum}'
    )


async def place_stops(command, args):
    data = await async_get_api_data(command)
    assets = get_current_prices(prepare_asset_data(data))
    levels = LEVELS[command]
    params = PARAMS[command]
    return await process_stops(assets, levels, STOPS_SUM, params)


async def process_nuke_command(command, args):
    args = parse_ticker_int_args(args)
    ticker, sum = args.ticker, args.sum
    ticker_data = parse_ticker_info(ticker)
    assets = get_current_prices(prepare_asset_data([ticker_data]))
    asset = assets[0]
    stop_sum = sum // 4
    if not sum_is_valid(asset, stop_sum):
        return 'Sum is too small, cancelling Nuke command'
    return await process_stops(assets, NUKE_LEVELS, stop_sum, LONG_STOP_PARAMS)
