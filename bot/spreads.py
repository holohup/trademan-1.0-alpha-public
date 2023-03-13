import asyncio
import logging
from datetime import datetime

from queue_handler import QUEUE
from settings import SLEEP_PAUSE
from tools.classes import Spread
from tools.get_patch_prepare_data import (async_get_api_data,
                                          async_patch_spread,
                                          prepare_spreads_data)

REPORT_ORDERS = False


def get_delta_prices(spread: Spread):
    return spread.far_leg.new_price - spread.near_leg.new_price * spread.ratio


def ok_to_place_order(spread):
    return (
        get_delta_prices(spread) > spread.price
        if spread.sell
        else get_delta_prices(spread) < spread.price
    )


async def safe_orders_cancel(spread):
    await asyncio.wait(
        [
            asyncio.create_task(spread.far_leg.cancel_order()),
            asyncio.create_task(spread.near_leg.cancel_order()),
        ]
    )
    await asyncio.wait(
        [
            spread.far_leg.update_executed(),
            spread.near_leg.update_executed(),
        ]
    )
    # await asyncio.gather(
    #     asyncio.create_task(spread.far_leg.cancel_order()),
    #     asyncio.create_task(spread.near_leg.cancel_order())
    # )
    # await asyncio.gather(
    #     asyncio.create_task(spread.far_leg.update_executed()),
    #     asyncio.create_task(spread.near_leg.update_executed())
    # )
    if spread.executed > 0:
        await async_patch_spread(spread)


async def cancel_active_orders_and_update_data(spreads):
    await asyncio.wait(
        [
            asyncio.create_task(safe_orders_cancel(spread))
            for spread in spreads
        ],
    )


async def wait_till_market_open(spread: Spread):
    if spread.far_leg.order_placed:
        await spread.far_leg.cancel_order()
    sleep_time = spread.seconds_till_trading_starts
    logging.warning(
        f'{spread}: Not a trading time. Waiting '
        f'for {sleep_time // 60} minutes.'
    )
    await asyncio.sleep(sleep_time)
    logging.warning(f'{spread}: Resuming session.')


async def get_spread_prices(spread):
    await asyncio.wait(
        [
            asyncio.create_task(spread.far_leg.get_price_from_order_book()),
            asyncio.create_task(spread.near_leg.get_price_from_order_book()),
        ]
    )


def far_leg_order_should_be_cancelled(spread: Spread):
    return spread.far_leg.order_placed and (
        spread.far_leg.new_price != spread.far_leg.last_price
        or not ok_to_place_order(spread)
    )


async def even_legs_execution(spread):
    await spread.far_leg.update_executed()
    await spread.even_execution()


async def place_new_far_leg_order(spread):
    if (
        not spread.far_leg.order_placed
        and spread.far_leg.next_order_amount >= spread.far_leg.lot
        and ok_to_place_order(spread)
    ):
        await spread.far_leg.place_sellbuy_order()
        if REPORT_ORDERS:
            await QUEUE.put(
                f'''{datetime.now().time()}: Spread far leg placed
                         {spread.far_leg.ticker}, \ndelta:
                          {get_delta_prices(spread)}, desired spread price:
                           {spread.price}, \n
                        placed {spread.far_leg.next_order_amount} at
                         price {spread.far_leg.new_price}'''
            )


async def patch_executed(spread, last_executed):
    if spread.executed > last_executed:
        await async_patch_spread(spread)
        await QUEUE.put(
            f'{spread}: executed [{spread.executed} '
            f'/ {spread.amount}] for {spread.avg_execution_price}'
        )
    return spread.executed


async def spread_trading_cycle(spread: Spread):
    if not spread.is_trading_now:
        await wait_till_market_open(spread)
    await get_spread_prices(spread)
    if far_leg_order_should_be_cancelled(spread):
        await spread.far_leg.cancel_order()
    await even_legs_execution(spread)
    await place_new_far_leg_order(spread)
    spread.far_leg.last_price = spread.far_leg.new_price


async def process_error(error, spread):
    await QUEUE.put(f'{spread}: {error}, waiting for 1 minute')
    await asyncio.sleep(60)


async def process_spread(spread: Spread):
    last_executed = spread.executed

    while spread.executed < spread.amount:
        try:
            await spread_trading_cycle(spread)
            last_executed = await patch_executed(spread, last_executed)
            await asyncio.sleep(SLEEP_PAUSE)

        except Exception as error:
            await process_error(error, spread)

    return spread


async def spreads(*args, **kwargs):
    spreads = prepare_spreads_data(await async_get_api_data('spreads'))
    if not spreads:
        return 'No active assets to sell or buy'
    try:
        print(f'Starting spreads: {spreads}')
        result = await asyncio.gather(
            *[
                asyncio.create_task(process_spread(spread), name=str(spread))
                for spread in spreads
            ]
        )
        return f'Торговля спредами завершена: {result}'

    except asyncio.CancelledError:
        await cancel_active_orders_and_update_data(spreads)
        result = '\n'.join(
            [
                f'{spread}: {spread.executed} for {spread.avg_execution_price}'
                for spread in spreads
                if spread.executed > 0
            ]
        )
        print('Stopping spreads')
        return f'Spreads routine cancelled. Executed: \n{result}'
