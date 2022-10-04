from tools.orders import get_current_orders
from tools.get_patch_prepare_data import async_get_api_data, prepare_asset_data
from decimal import Decimal, getcontext

async def orders():
    return await get_current_orders()


async def test():
    assets = prepare_asset_data(await async_get_api_data('sellbuy'))

    # getcontext().prec = 10

    return [(100 - asset.increment, 100 + asset.increment) for asset in assets]