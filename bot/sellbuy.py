import asyncio

from queue_handler import QUEUE
from settings import SLEEP_PAUSE
from tools.classes import Asset
from tools.get_patch_prepare_data import (async_get_api_data,
                                          async_patch_sellbuy,
                                          prepare_assets_data)


async def sellbuy_cycle(asset):
    await asset.get_price_from_order_book()
    if asset.new_price != asset.last_price and asset.order_placed:
        await asset.cancel_order()
    if asset.order_id:
        await asset.update_executed()
    if not asset.order_placed and asset.next_order_amount >= asset.lot:
        await asset.place_sellbuy_order()


async def process_asset(asset):
    last_executed = asset.executed

    while asset.next_order_amount >= asset.lot:
        try:
            await sellbuy_cycle(asset)
            asset.last_price = asset.new_price
            if last_executed < asset.executed:
                await async_patch_sellbuy(asset)
                last_executed = asset.executed
            await asyncio.sleep(SLEEP_PAUSE)

        except Exception as error:
            await QUEUE.put(error)

    return (
        f'Sellbuy for {asset.ticker} finished: {asset.executed}'
        f' for {asset.avg_exec_price}'
    )


async def safe_order_cancel(asset: Asset):
    if asset.order_placed:
        await asset.cancel_order()
    if asset.order_id:
        await asset.update_executed()
    if asset.executed > 0:
        await async_patch_sellbuy(asset)


async def sellbuy(command, args):
    assets = prepare_assets_data(await async_get_api_data('sellbuy'))
    if not assets:
        return 'No active assets to sell or buy'
    try:
        print(f'Starting sellbuy: {assets}')
        result = await asyncio.gather(
            *[
                asyncio.create_task(process_asset(asset), name=asset.ticker)
                for asset in assets
            ]
        )
        return f'''Покупка-продажа завершены.
         Исполнены заявки по инструментам: {result}'''

    except asyncio.CancelledError:
        await asyncio.wait([asyncio.create_task(
            safe_order_cancel(asset)
        ) for asset in assets
        ])
        executed_tickers = [
            f'{asset.ticker}: {asset.executed} for {asset.avg_exec_price}'
            for asset in assets
            if asset.executed > 0
        ]
        if not executed_tickers:
            executed_tickers = None
        return f'''SellBuy routine stopped.
        Already executed: {executed_tickers}.'''
