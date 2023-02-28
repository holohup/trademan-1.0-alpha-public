import asyncio

from aiogram import types
from bot_init import dp
from cancel_all_orders import cancel_orders
from grpc.aio._call import AioRpcError
from instant_commands import (check_health, get_current_spread_prices, help,
                              test)
from place_stops import (place_long_stops, place_short_stops,
                         process_nuke_command)
from restore_stops import restore_stops
from sellbuy import sellbuy
from spreads import spreads

RUNNING_TASKS = {}


async def stop_running_tasks(*args, **kwargs):
    to_stop = RUNNING_TASKS.copy()
    for task, coro in to_stop.items():
        if task != 'Cancel':
            if coro.cancel():
                RUNNING_TASKS.pop(task)
    return f'Finished stopping. Running tasks: {RUNNING_TASKS}'


async def cancel_all_orders(*args, **kwargs):
    await asyncio.gather(
        asyncio.create_task(stop_running_tasks()),
        asyncio.create_task(cancel_orders()),
    )
    return 'All tasks stopped, all orders cancelled'


async def tasks(*args, **kwargs):
    tasks = ', '.join(
        [task for task in RUNNING_TASKS.keys() if task != 'Tasks']
    ) if RUNNING_TASKS else 'None'
    return f'Running tasks: {tasks}'


ROUTINES = {
    'sprices': ('Current spread prices', get_current_spread_prices),
    'test': ('Testing current tests', test),
    'stops': ('Placing long stops', place_long_stops),
    'nuke': ('Nuke', process_nuke_command),
    'shorts': ('Placing short stops', place_short_stops),
    'restore': ('Restoring stop orders', restore_stops),
    'sellbuy': ('SellBuy', sellbuy),
    'spreads': ('Spreads monitoring and trading', spreads),
    'help': ('Help', help),
    'stop': ('Stopping tasks', stop_running_tasks),
    'cancel': ('Cancel', cancel_all_orders),
    'tasks': ('Tasks', tasks),
}


@dp.message_handler(commands=ROUTINES.keys(), is_me=True)
async def generic_handler(message: types.Message):
    title, executor = ROUTINES[message.get_command().lstrip('/')]
    await command_handler(title, executor, message)


async def command_handler(title: str, func, message: types.Message):
    if title in RUNNING_TASKS:
        await message.answer(f'{title} already running!')
        return

    if not await check_health():
        await message.answer('Server not working!')
        return

    await message.answer(title)
    result = asyncio.create_task(func(message.text))
    RUNNING_TASKS[title] = result
    try:
        await result
    except (AioRpcError, AttributeError, ValueError) as error:
        await message.answer(f'Error executing {title}: {error}')
    else:
        await message.answer(result.result())
    finally:
        if title in RUNNING_TASKS:
            RUNNING_TASKS.pop(title)
