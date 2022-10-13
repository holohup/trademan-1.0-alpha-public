import asyncio

from spreads import get_delta_prices
from tools.get_patch_prepare_data import async_get_api_data, prepare_asset_data, prepare_spreads_data
from tools.orders import get_current_orders


async def orders():
    return await get_current_orders()


async def test():
    assets = prepare_asset_data(await async_get_api_data('sellbuy'))
    return [(100 - asset.increment, 100 + asset.increment) for asset in assets]


async def get_current_spread_prices():
    spreads = prepare_spreads_data(await async_get_api_data('spreads'))
    if not spreads:
        return 'No active assets to sell or buy'
    await asyncio.gather(
        *[
            asyncio.create_task(spread.far_leg.get_price_to_place_order())
            for spread in spreads
        ],
        *[
            asyncio.create_task(spread.near_leg.get_closest_execution_price())
            for spread in spreads
        ],
    )
    result = ''
    for spread in spreads:
        result += f'{spread}: current: {get_delta_prices(spread)}, desired: {spread.price}\n'
    return result
