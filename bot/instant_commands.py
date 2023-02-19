import asyncio

import aiohttp.client_exceptions
from queue_handler import QUEUE
from spreads import get_delta_prices
from tools.get_patch_prepare_data import (async_check_health,
                                          async_get_api_data,
                                          prepare_spreads_data)
from tools.orders import get_current_orders


async def orders():
    return await get_current_orders()


async def test():
    result = await check_health()
    return result


async def check_health():
    try:
        result = await async_check_health()
    except (TimeoutError, OSError, aiohttp.client_exceptions.ClientError):
        return False
    else:
        return result == 200


async def get_current_spread_prices():
    spreads = prepare_spreads_data(await async_get_api_data('spreads'))
    if not spreads:
        return 'No active assets to sell or buy'
    try:
        await asyncio.gather(
            *[asyncio.create_task(spread.far_leg.get_price_to_place_order()) for spread in spreads],
            *[asyncio.create_task(spread.near_leg.get_closest_execution_price()) for spread in spreads],
        )
    except ValueError as error:
        await QUEUE.put(error)
    result = ''
    for spread in spreads:
        result += f'{spread}: current: {get_delta_prices(spread)}\n'
    return result
