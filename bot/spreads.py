from tools.get_patch_prepare_data import prepare_spreads_data, async_get_api_data, async_patch_executed
import asyncio
from tools.utils import perform_working_hours_check, get_seconds_till_open
import logging
from tools.classes import Spread
from settings import SLEEP_PAUSE
from datetime import datetime


def get_delta_prices(spread: Spread):
    if spread.near_leg_type == 'S':
        return spread.far_leg.new_price - spread.near_leg.closest_execution_price * spread.base_asset_amount
    return spread.far_leg.new_price - spread.near_leg.closest_execution_price


def ok_to_place_order(spread):
    if spread.sell:
        return get_delta_prices(spread) > spread.price
    return get_delta_prices(spread) < spread.price


async def process_spread(spread):
    last_executed = spread.executed
    while spread.executed < spread.amount:
        if perform_working_hours_check():
            await asyncio.gather(asyncio.create_task(spread.far_leg.get_price_to_place_order()),
                                 asyncio.create_task(spread.near_leg.get_closest_execution_price()))

            if spread.far_leg.new_price != spread.far_leg.last_price and spread.far_leg.order_placed:
                await spread.far_leg.cancel_order()
            else:
                logging.info(f'Price unchanged, not cancelling the order for {spread.far_leg.ticker}.')

            if spread.far_leg.order_id:
                await spread.far_leg.update_executed()
                await spread.even_execution()

            if (
                not spread.far_leg.order_placed
                and spread.far_leg.next_order_amount >= spread.far_leg.lot
                and ok_to_place_order(spread)
            ):
                await spread.far_leg.place_sellbuy_order()
                print(f'{datetime.now().time()}: Spread placed {spread}, delta: {get_delta_prices(spread)}, price: {spread.price}')

            spread.far_leg.last_price = spread.far_leg.new_price
            if spread.executed > last_executed:
                await asyncio.create_task(async_patch_executed('spreads', spread.id, spread.executed))
            last_executed = spread.executed
            await asyncio.gather(asyncio.create_task(asyncio.sleep(SLEEP_PAUSE)))

        else:
            sleep_time = get_seconds_till_open()
            logging.warning(f'Not a trading time. Waiting for {sleep_time // 60} minutes.')
            await asyncio.sleep(sleep_time)
            logging.warning(f'Resuming session.')

    await async_patch_executed('spreads', spread.id, spread.executed)
    return spread


async def spreads():
    spreads = prepare_spreads_data(await async_get_api_data('spreads'))
    if not spreads:
        return 'No active assets to sell or buy'
    try:
        print(f'Starting spreads: {spreads}')
        result = await asyncio.gather(
            *[asyncio.create_task(process_spread(spread), name=str(spread)) for spread in spreads])
        return f'Торговля спредами завершена: {result}'

    except asyncio.CancelledError as error:
        await asyncio.gather(
            *[asyncio.create_task(spread.near_leg.cancel_order()) for spread in spreads if spread.near_leg.order_placed],
            *[asyncio.create_task(spread.far_leg.cancel_order()) for spread in spreads if spread.far_leg.order_placed]
        )
        await asyncio.gather(
            *[asyncio.create_task(spread.near_leg.update_executed()) for spread in spreads if spread.near_leg.order_id],
            *[asyncio.create_task(spread.far_leg.update_executed()) for spread in spreads if spread.far_leg.order_id]
        )

        await asyncio.gather(
            *[asyncio.create_task(
                async_patch_executed('spreads', spread.id, spread.executed)
            ) for spread in spreads if spread.executed > 0]
        )
        result = {str(spread): spread.executed for spread in spreads if spread.executed > 0}
        print('Stopping spreads')
        return f'Spreads routine cancelled. Status: {result}.'
