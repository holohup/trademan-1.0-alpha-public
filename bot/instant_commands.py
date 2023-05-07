import asyncio
from http import HTTPStatus

import aiohttp.client_exceptions
from spreads import get_delta_prices, get_spread_prices
from tools.classes import Asset
from tools.get_patch_prepare_data import (async_check_health,
                                          async_get_api_data,
                                          prepare_spreads_data)


async def test(command, args):
    from decimal import Decimal

    from tools.get_patch_prepare_data import async_patch_sellbuy

    s = Asset(
        ticker='', figi='', min_price_increment=Decimal('0'), lot=0, id=1
    )
    s.order_cache.update('1', 50, Decimal('100'))
    return await async_patch_sellbuy(s)


async def check_health(*args, **kwargs):
    try:
        result = await async_check_health() == HTTPStatus.OK
    except (TimeoutError, OSError, aiohttp.client_exceptions.ClientError):
        result = False
    return result


async def get_spread_price(spread):
    try:
        await get_spread_prices(spread)
    except (ValueError, AttributeError) as error:
        return f'{spread}:, {error}'
    return f'{spread}: current: {get_delta_prices(spread)}'


async def get_current_spread_prices(command, args):
    spreads = prepare_spreads_data(await async_get_api_data('spreads'))
    if not spreads:
        return 'No active assets to sell or buy'
    result = await asyncio.gather(
        *[
            asyncio.create_task(get_spread_price(spread))
            for spread in spreads
            if spread.is_trading_now
        ],
    )
    not_trading = ', '.join(
        [
            '\n'
            + str(spread)
            + f' t = {spread.seconds_till_trading_starts // 60} min'
            for spread in spreads
            if not spread.is_trading_now
        ]
    )
    return '\n'.join(result) + f'\nCurrently not trading: {not_trading}'


async def help(command, args):
    return (
        'Bot is operational! The commands are:\n'
        'stops, shorts,\n'
        'restore, sellbuy,\n'
        'monitor,\n'
        'stop, cancel'
    )
