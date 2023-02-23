import asyncio

from aiogram import types
from bot_init import dp
from cancel_all_orders import cancel_orders
from grpc.aio._call import AioRpcError
from instant_commands import (check_health, get_current_orders,
                              get_current_spread_prices, test)
from place_stops import (place_long_stops, place_short_stops,
                         process_nuke_command)
from restore_stops import restore_stops
from sellbuy import sellbuy
from spreads import spreads

RUNNING_TASKS = {}


def stop_running_tasks():
    to_stop = RUNNING_TASKS.copy()
    for task, coro in to_stop.items():
        coro.cancel()
        RUNNING_TASKS.pop(task)


@dp.message_handler(commands=['start', 'help'], is_me=True)
async def help_handler(message: types.Message):
    await message.answer(
        'Bot is operational! The commands are:\n'
        'stops, shorts,\n'
        'restore, sellbuy,\n'
        'monitor,\n'
        'stop, cancel'
    )


@dp.message_handler(commands=['stop'], is_me=True)
async def stop_handler(message: types.Message):
    while RUNNING_TASKS:
        stop_running_tasks()
    await message.answer(f'Finished stopping. Running tasks: {RUNNING_TASKS}')


@dp.message_handler(commands=['tasks'], is_me=True)
async def tasks_handler(message: types.Message):
    tasks = ', '.join([task for task in RUNNING_TASKS.keys()])
    await message.answer(f'Running tasks: {tasks}')


@dp.message_handler(commands=['cancel'], is_me=True)
async def cancel_all_orders_handler(message: types.Message):
    while RUNNING_TASKS:
        stop_running_tasks()
    await trades_handler(
        'Cancelling all active orders', cancel_orders, message
    )


@dp.message_handler(commands=['orders'], is_me=True)
async def orders_handler(message: types.Message):
    await trades_handler(
        'Retrieving current orders', get_current_orders, message
    )


@dp.message_handler(commands=['sprices'], is_me=True)
async def spreads_prices_handler(message: types.Message):
    await trades_handler(
        'Current spread prices:', get_current_spread_prices, message
    )


@dp.message_handler(commands=['test'], is_me=True)
async def test_handler(message: types.Message):
    await trades_handler('Testing current tests!', test, message)


async def trades_handler(greeting: str, func, message: types.Message):
    if greeting in RUNNING_TASKS:
        await message.answer(f'{greeting} already running!')
        return

    if not await check_health():
        await message.answer('Server not working!')
        return

    await message.answer(greeting)
    result = asyncio.create_task(func(message.text))
    RUNNING_TASKS[greeting] = result
    try:
        await result
    except (AioRpcError, AttributeError, ValueError) as error:
        await message.answer(f'Error executing {greeting}: {error}')
    else:
        await message.answer(result.result())
    finally:
        if greeting in RUNNING_TASKS:
            RUNNING_TASKS.pop(greeting)


@dp.message_handler(commands=['stops'], is_me=True)
async def place_long_stops_handler(message: types.Message):
    await trades_handler('Placing long stops', place_long_stops, message)


@dp.message_handler(commands=['nuke'], is_me=True)
async def nuke_handler(message: types.Message):
    await trades_handler(
        'Processing nuke command', process_nuke_command, message
    )


@dp.message_handler(commands=['shorts'], is_me=True)
async def place_short_stops_handler(message: types.Message):
    await trades_handler('Placing short stops', place_short_stops, message)


@dp.message_handler(commands=['restore'], is_me=True)
async def restore_stops_handler(message: types.Message):
    await trades_handler('Restoring stop orders', restore_stops, message)


@dp.message_handler(commands=['sellbuy'], is_me=True)
async def sellbuy_handler(message: types.Message):
    await trades_handler(
        'Selling and buying stocks from the list', sellbuy, message
    )


@dp.message_handler(commands=['spreads'], is_me=True)
async def spreads_handler(message: types.Message):
    await trades_handler('Spreads monitoring and trading', spreads, message)


@dp.message_handler(commands=['status', 'stats', 'hello'], is_me=True)
async def status_handler(message: types.Message):
    await message.answer('Working...')
