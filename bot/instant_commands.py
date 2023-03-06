import asyncio
from http import HTTPStatus

import aiohttp.client_exceptions
from spreads import get_delta_prices, get_spread_prices
from tools.classes import Asset, Spread
from tools.get_patch_prepare_data import (async_check_health,
                                          async_get_api_data,
                                          prepare_spreads_data)


async def test(*args, **kwargs):
    from decimal import Decimal

    from tools.get_patch_prepare_data import async_patch_spread

    f = Asset(ticker='', figi='', increment=0, lot=0)
    n = Asset(ticker='', figi='', increment=0, lot=0)
    sp = Spread(
        id=3, far_leg=f, near_leg=n, sell=True, price=0, ratio=0, amount=0
    )
    sp.far_leg.order_cache.update('1', 100, Decimal('100'))
    sp.near_leg.order_cache.update('2', 300, Decimal('300'))
    print(sp.avg_execution_price)
    result = await async_patch_spread(sp)
    print(result)
    return await check_health()


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


async def get_current_spread_prices(*args, **kwargs):
    spreads = prepare_spreads_data(await async_get_api_data('spreads'))
    if not spreads:
        return 'No active assets to sell or buy'
    result = await asyncio.gather(
        *[asyncio.create_task(get_spread_price(spread)) for spread in spreads],
    )
    return '\n'.join(result)


async def help(*args, **kwargs):
    return (
        'Bot is operational! The commands are:\n'
        'stops, shorts,\n'
        'restore, sellbuy,\n'
        'monitor,\n'
        'stop, cancel'
    )
