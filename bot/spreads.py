import asyncio
import logging
from datetime import datetime

from queue_handler import QUEUE
from settings import SLEEP_PAUSE
from tinkoff.invest.exceptions import RequestError
from tools.classes import Spread
from tools.get_patch_prepare_data import (async_get_api_data,
                                          async_patch_executed,
                                          prepare_spreads_data)
from tools.utils import get_seconds_till_open, perform_working_hours_check

REPORT_ORDERS = False


def get_delta_prices(spread: Spread):
    if (
        spread.near_leg.ticker == 'USDRUBF' and spread.far_leg.ticker == 'SiZ2'
    ):  # TODO: ЗАГЛУШКА! Переписать.
        return (
            spread.far_leg.new_price
            - spread.near_leg.closest_execution_price
            * spread.base_asset_amount
        )
    if spread.near_leg_type == 'S':
        return (
            spread.far_leg.new_price
            - spread.near_leg.closest_execution_price
            * spread.base_asset_amount
        )
    return spread.far_leg.new_price - spread.near_leg.closest_execution_price


def ok_to_place_order(spread):
    return (
        get_delta_prices(spread) > spread.price
        if spread.sell
        else get_delta_prices(spread) < spread.price
    )


async def cancel_active_orders_and_update_data(spreads):
    await asyncio.gather(
        *[
            asyncio.create_task(spread.near_leg.cancel_order())
            for spread in spreads
            if spread.near_leg.order_placed
        ],
        *[
            asyncio.create_task(spread.far_leg.cancel_order())
            for spread in spreads
            if spread.far_leg.order_placed
        ],
    )
    await asyncio.gather(
        *[
            asyncio.create_task(spread.near_leg.update_executed())
            for spread in spreads
            if spread.near_leg.order_id
        ],
        *[
            asyncio.create_task(spread.far_leg.update_executed())
            for spread in spreads
            if spread.far_leg.order_id
        ],
    )
    await asyncio.gather(
        *[
            asyncio.create_task(
                async_patch_executed(
                    'spreads',
                    spread.id,
                    spread.executed,
                    spread.avg_execution_price,
                )
            )
            for spread in spreads
            if spread.executed > 0
        ]
    )


async def wait_till_market_open(spread):
    sleep_time = get_seconds_till_open()
    logging.warning(
        f'''{spread}: Not a trading time.
            Waiting for {sleep_time // 60} minutes.'''
    )
    await asyncio.gather(
        asyncio.create_task(asyncio.sleep(sleep_time)),
        asyncio.create_task(cancel_active_orders_and_update_data([spread])),
    )
    logging.warning(f'{spread}: Resuming session.')


async def get_spread_prices(spread):
    await asyncio.gather(
        asyncio.create_task(spread.far_leg.get_price_to_place_order()),
        asyncio.create_task(spread.near_leg.get_closest_execution_price()),
    )


async def adjust_placed_order(spread):
    if not spread.far_leg.order_placed:
        return
    if (
        spread.far_leg.new_price != spread.far_leg.last_price
        or not ok_to_place_order(spread)
    ):
        await spread.far_leg.cancel_order()
    else:
        logging.info(
            f'''Prices unchanged, not cancelling
            the order for {spread.far_leg.ticker}.'''
        )
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
        await async_patch_executed(
            'spreads',
            spread.id,
            spread.executed,
            spread.avg_execution_price,
        )
        await QUEUE.put(
            f'''{spread}: executed [{spread.executed} /
                {spread.amount}] for
                {spread.avg_execution_price}'''
        )
    return spread.executed


async def process_spread(spread):
    last_executed = spread.executed

    while spread.executed < spread.amount:
        if not perform_working_hours_check():
            await wait_till_market_open(spread)

        try:
            await get_spread_prices(spread)
            await adjust_placed_order(spread)
            await place_new_far_leg_order(spread)
            spread.far_leg.last_price = spread.far_leg.new_price
            last_executed = await patch_executed(spread, last_executed)
            await asyncio.sleep(SLEEP_PAUSE)

        except AttributeError:
            await QUEUE.put(
                f'{spread}: ratelimit_reset error, waiting for 1 minute'
            )
            await asyncio.sleep(60)
            print(f'continuing with {spread}')

        except RequestError as error:
            await QUEUE.put(
                f'''{spread} RequestError: msg:
                 {error.metadata.message}, details:
                  {error.details}, code: {error.code},
                   md: {error.metadata}'''
            )

        except Exception as error:
            await QUEUE.put(f'[{spread}]: {error}. Waiting for 60 secs.')
            await asyncio.sleep(60)

    await async_patch_executed(
        'spreads', spread.id, spread.executed, spread.avg_execution_price
    )
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
        result = {
            str(spread): (spread.executed, spread.avg_execution_price)
            for spread in spreads
            if spread.executed > 0
        }
        print('Stopping spreads')
        return f'Spreads routine stopped. Status: {result}.'
