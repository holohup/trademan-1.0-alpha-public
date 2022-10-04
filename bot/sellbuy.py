from tools.get_patch_prepare_data import prepare_asset_data, async_get_api_data, async_patch_executed
from tools.utils import perform_working_hours_check, get_seconds_till_open
import logging
import asyncio


async def main():
    assets = prepare_asset_data(await async_get_api_data('sellbuy'))
    result = asyncio.create_task(sellbuy(assets))
    print(assets)
    return await result

async def pprint(str):
    print(str)

async def sellbuy(assets: list):
    if not assets:
        return 'No active assets to sell or buy'
    executed_tickers = {}
    try:
        while assets:
            print(f'Remaining assets: {assets}')
            if perform_working_hours_check():
                result = await asyncio.gather(
                    *[asyncio.create_task(asset.get_price_to_place_order()) for asset in assets]
                )

                for asset in assets:
                    asset.new_price = result.pop(0)

                await asyncio.gather(
                    *[asyncio.create_task(
                        asset.cancel_order()
                    ) for asset in assets if asset.new_price != asset.last_price and asset.order_id]
                )
                for asset in assets:
                    if asset.last_price == asset.new_price:
                        logging.info(f'Price unchanged, not cancelling the order for {asset.ticker}.')

                    # if asset.order_id:
                    #     await asset.update_executed()
                    #
                    # if not asset.order_placed and asset.next_order_amount >= asset.lot:
                    #     logging.info('Пытаемся поставить заявку')
                    #     try:
                    #         await asset.place_sellbuy_order(asset.new_price)
                    #     except Exception as error:
                    #         logging.error(f'Не удается поставить заявку! {error}')
                    #         raise ConnectionError(f'{error}')
                    # if asset.next_order_amount < asset.lot:
                    #     await async_patch_executed('sellbuy', asset.id, asset.executed)
                    #     executed_tickers[asset.ticker] = asset.executed
                    #     assets.remove(asset)
                    #
                    # asset.last_price = asset.new_price
            else:
                sleep_time = get_seconds_till_open()
                logging.info(f'Not a trading time. Waiting for {sleep_time // 60} minutes.')
                await asyncio.sleep(sleep_time)

        return f'Покупка-продажа завершены. Исполнены заявки по инструментам: {executed_tickers}'
    except asyncio.CancelledError as error:
        for asset in assets:
            if asset.order_placed:
                await asset.cancel_order()
        return f'SellBuy routine cancelled. Lots already executed: {executed_tickers}.'

if __name__ == '__main__':
    print(asyncio.run(main()))