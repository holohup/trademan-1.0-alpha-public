from aiogram import types
import asyncio
from bot_init import dp
import place_stops
import cancel_all_orders

RUNNING_TASKS = []


def stop_running_tasks():
    for task in RUNNING_TASKS:
        task.cancel()
        RUNNING_TASKS.remove(task)


@dp.message_handler(commands=['start', 'help'], is_me=True)
async def help_handler(message: types.Message):
    await message.answer('hello!')

@dp.message_handler(commands=['stop'], is_me=True)
async def stop_handler(message: types.Message):
    while RUNNING_TASKS:
        stop_running_tasks()
    await message.answer(f'Finished stopping. Running tasks: {RUNNING_TASKS}')


@dp.message_handler(commands=['cancel'], is_me=True)
async def cancel(message: types.Message):
    while RUNNING_TASKS:
        stop_running_tasks()
    await message.answer('Cancelling all active orders')
    result = asyncio.create_task(cancel_all_orders.cancel_orders())
    await result
    await message.answer(result.result())


@dp.message_handler(commands=['stops'], is_me=True)
async def place_lng_stops(message: types.Message):
    await message.answer('placing stops')
    result = asyncio.create_task(place_stops.place_long_stops())
    RUNNING_TASKS.append(result)
    await result
    if result in RUNNING_TASKS:
        RUNNING_TASKS.remove(result)
    await message.answer(result.result())


@dp.message_handler(commands=['shorts'], is_me=True)
async def place_shrt_stops(message: types.Message):
    await message.answer('placing short stops')
    result = asyncio.create_task(place_stops.place_short_stops())
    RUNNING_TASKS.append(result)
    await result
    if result in RUNNING_TASKS:
        RUNNING_TASKS.remove(result)
    await message.answer(result.result())
