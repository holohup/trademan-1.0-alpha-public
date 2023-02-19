import asyncio
import logging

from queue_handler import QUEUE
from settings import SLEEP_PAUSE
from tools.get_patch_prepare_data import (async_get_api_data,
                                          async_patch_executed,
                                          prepare_asset_data)


async def process_asset(asset):

    while asset.next_order_amount >= asset.lot:
        try:
            await asset.get_price_to_place_order()
            if asset.new_price != asset.last_price and asset.order_placed:
                await asset.cancel_order()
            else:
                logging.info(
                    f'Price unchanged, not cancelling the order for {asset.ticker}.'
                )
            if asset.order_id:
                await asset.update_executed()
            if not asset.order_placed and asset.next_order_amount >= asset.lot:
                await asset.place_sellbuy_order()

            asset.last_price = asset.new_price
            await asyncio.gather(
                asyncio.create_task(asyncio.sleep(SLEEP_PAUSE)),
                asyncio.create_task(
                    async_patch_executed('sellbuy', asset.id, asset.executed)
                ),
            )
        except Exception as error:
            await QUEUE.put(error)

    await async_patch_executed('sellbuy', asset.id, asset.executed)
    await QUEUE.put(f'Sellbuy for {asset.ticker} finished')
    return {asset.ticker: asset.executed}


async def sellbuy():
    assets = prepare_asset_data(await async_get_api_data('sellbuy'))
    if not assets:
        return 'No active assets to sell or buy'
    try:
        print(f'Starting assets: {assets}')
        result = await asyncio.gather(
            *[asyncio.create_task(process_asset(asset), name=asset.ticker) for asset in assets]
        )
        return f'Покупка-продажа завершены. Исполнены заявки по инструментам: {result}'
    except asyncio.CancelledError:
        await asyncio.gather(
            *[asyncio.create_task(asset.cancel_order()) for asset in assets if asset.order_placed]
        )
        await asyncio.gather(
            *[asyncio.create_task(asset.update_executed()) for asset in assets if asset.order_id]
        )
        await asyncio.gather(
            *[asyncio.create_task(async_patch_executed('sellbuy', asset.id, asset.executed))
                for asset in assets if asset.executed > 0]
        )
        executed_tickers = {asset.ticker: asset.executed for asset in assets if asset.executed > 0}
        return f'SellBuy routine cancelled. Lots already executed: {executed_tickers}.'
