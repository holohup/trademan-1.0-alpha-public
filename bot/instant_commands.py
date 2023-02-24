import asyncio

import aiohttp.client_exceptions
from queue_handler import QUEUE
from spreads import get_delta_prices
from tools.get_patch_prepare_data import (async_check_health,
                                          async_get_api_data,
                                          prepare_spreads_data)


async def test(*args, **kwargs):
    return await check_health()


async def check_health(*args, **kwargs):
    try:
        result = await async_check_health()
    except (TimeoutError, OSError, aiohttp.client_exceptions.ClientError):
        return False
    else:
        return result == 200


async def get_current_spread_prices(*args, **kwargs):
    spreads = prepare_spreads_data(await async_get_api_data('spreads'))
    if not spreads:
        return 'No active assets to sell or buy'
    try:
        await asyncio.gather(
            *[
                asyncio.create_task(spread.far_leg.get_price_to_place_order())
                for spread in spreads
            ],
            *[
                asyncio.create_task(
                    spread.near_leg.get_closest_execution_price()
                )
                for spread in spreads
            ],
        )
    except ValueError as error:
        await QUEUE.put(error)
    result = ''
    for spread in spreads:
        result += f'{spread}: current: {get_delta_prices(spread)}\n'
    return result


async def help(*args, **kwargs):
    return (
        'Bot is operational! The commands are:\n'
        'stops, shorts,\n'
        'restore, sellbuy,\n'
        'monitor,\n'
        'stop, cancel'
    )
