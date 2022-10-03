from aiogram import types
import asyncio
from bot_init import dp
from place_stops import place_short_stops, place_long_stops
from cancel_all_orders import cancel_orders
from restore_stops import restore_stops
from sellbuy import sellbuy
# from monitor import monitor

RUNNING_TASKS = []


def stop_running_tasks():
    for task in RUNNING_TASKS:
        task.cancel()
        RUNNING_TASKS.remove(task)


@dp.message_handler(commands=['start', 'help'], is_me=True)
async def help_handler(message: types.Message):
    await message.answer('Bot is operational! The commands are:\n'
                         'stops, shorts,\n'
                         'restore, sellbuy,\n'
                         'monitor,\n'
                         'stop, cancel')


@dp.message_handler(commands=['stop'], is_me=True)
async def stop_handler(message: types.Message):
    while RUNNING_TASKS:
        stop_running_tasks()
    await message.answer(f'Finished stopping. Running tasks: {RUNNING_TASKS}')


@dp.message_handler(commands=['cancel'], is_me=True)
async def cancel_all_orders_handler(message: types.Message):
    while RUNNING_TASKS:
        stop_running_tasks()
    await trades_handler('Cancelling all active orders', cancel_orders(), message)


async def trades_handler(greeting: str, func, message: types.Message):
    await message.answer(greeting)
    result = asyncio.create_task(func)
    RUNNING_TASKS.append(result)
    await result
    if result in RUNNING_TASKS:
        RUNNING_TASKS.remove(result)
    await message.answer(result.result())


@dp.message_handler(commands=['stops'], is_me=True)
async def place_long_stops_handler(message: types.Message):
    await trades_handler('Placing long stops', place_long_stops(), message)


@dp.message_handler(commands=['shorts'], is_me=True)
async def place_short_stops_handler(message: types.Message):
    await trades_handler('Placing short stops', place_short_stops(), message)


@dp.message_handler(commands=['restore'], is_me=True)
async def restore_stops_handler(message: types.Message):
    await trades_handler('Restoring stop orders', restore_stops(), message)


@dp.message_handler(commands=['sellbuy'], is_me=True)
async def sellbuy_handler(message: types.Message):
    await trades_handler('Selling and buying stocks from the list', sellbuy(), message)


@dp.message_handler(commands=['status', 'stats', 'hello'], is_me=True)
async def status_handler(message: types.Message):
    await message.answer('Working...')


@dp.message_handler(commands=['monitor'], is_me=True)
async def sellbuy_handler(message: types.Message):
    await trades_handler('Starting spreads monitoring', monitor(), message)

