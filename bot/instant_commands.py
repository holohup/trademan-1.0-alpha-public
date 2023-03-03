import asyncio
from http import HTTPStatus

import aiohttp.client_exceptions
from spreads import get_delta_prices, get_spread_prices
from tools.get_patch_prepare_data import (async_check_health,
                                          async_get_api_data,
                                          prepare_spreads_data)


async def test(*args, **kwargs):
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
    except ValueError as error:
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
