import asyncio
from urllib.error import HTTPError

from aiogram import types
from bot_init import dp
from cancel_all_orders import cancel_orders
from grpc.aio._call import AioRpcError
from instant_commands import (check_health, get_current_spread_prices, help,
                              test)
from place_stops import place_stops, process_nuke_command
from scanner.scanner import dividend_scan, scan
from sellbuy import sellbuy
from spreads import spreads
from stop_orders import restore_stops, save_stops

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
    )
    if not tasks:
        tasks = 'None'
    return f'Running tasks: {tasks}'


ROUTINES = {
    'sprices': ('Current spread prices', get_current_spread_prices),
    'test': ('Testing current tests', test),
    'stops': ('Placing long stops', place_stops),
    'nuke': ('Nuke', process_nuke_command),
    'shorts': ('Placing short stops', place_stops),
    'stash': ('Saving stop orders to db', save_stops),
    'restore': ('Restoring stop orders', restore_stops),
    'sellbuy': ('SellBuy', sellbuy),
    'spreads': ('Spreads monitoring and trading', spreads),
    'help': ('Help', help),
    'stop': ('Stopping tasks', stop_running_tasks),
    'cancel': ('Cancel', cancel_all_orders),
    'tasks': ('Tasks', tasks),
    'health': ('Health check', check_health),
    'sell': ('Sell ASAP', sellbuy),
    'buy': ('Buy ASAP', sellbuy),
    'dump': ('Dump it', sellbuy),
    'scan': ('Spread scanner', scan),
    'dscan': ('Dividend scanner', dividend_scan)
}


@dp.message_handler(commands=ROUTINES.keys(), is_me=True)
async def generic_handler(message: types.Message):
    command_handler = CommandHandler(message)
    await command_handler.handle()


class CommandHandler:
    def __init__(self, message: types.Message) -> None:
        self._message = message
        self._command = message.get_command(pure=True)
        self._args = message.get_args()
        if not self._command:
            raise KeyError('Please provide a command.')
        self._title, self._routine = ROUTINES[self._command]
        self._result = ''

    async def handle(self):
        if await self._ok_to_start_executing():
            await self._process_command()
        await self._message.answer(self._result)

    async def _ok_to_start_executing(self):
        if self._title in RUNNING_TASKS:
            self._result = f'{self._title} already running!'
            return False

        if not await check_health(self._command, self._args):
            self._result = 'Server not working!'
            return False
        return True

    async def _process_command(self):
        await self._message.answer(self._title)
        result = asyncio.create_task(self._routine(self._command, self._args))
        RUNNING_TASKS[self._title] = result
        try:
            await result
        except (
            AioRpcError,
            AttributeError,
            ValueError,
            HTTPError,
            ConnectionError,
            KeyError
        ) as error:
            self._result = f'Error executing {self._title}: {error}'
        else:
            self._result = result.result()
        finally:
            if self._title in RUNNING_TASKS:
                RUNNING_TASKS.pop(self._title)
