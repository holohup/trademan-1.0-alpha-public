import asyncio
import logging
import sys

import commands
from aiogram import executor
from bot_init import dp
from queue_handler import QUEUE, worker
from settings import (TCS_ACCOUNT_ID, TCS_RO_TOKEN, TCS_RW_TOKEN,
                      TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)

__all__ = ('commands',)


async def send_greetings():
    await QUEUE.put('Battlecruiser operational.')


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.WARNING,
        format=(
            '%(asctime)s [%(levelname)s] '
            '%(filename)s >> %(lineno)d '
            '[%(message)s]'
        ),
        handlers=[logging.StreamHandler(stream=sys.stdout)]
    )

    if not all(
            [
                TCS_RO_TOKEN,
                TCS_RW_TOKEN,
                TCS_ACCOUNT_ID,
                TELEGRAM_TOKEN,
                TELEGRAM_CHAT_ID,
            ]
    ):
        message = (
            'Не удалось загрузить все переменные из окружения. Переменные:\n'
            f'TCS_ACCOUNT_ID: {TCS_ACCOUNT_ID}\n'
            f'TCS_RW_TOKEN: {TCS_RW_TOKEN}\n'
            f'TCS_RO_TOKEN: {TCS_RO_TOKEN}\n'
            f'TELEGRAM_TOKEN: {TELEGRAM_TOKEN}\n'
            f'TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}'
        )
        logging.critical(message)
        sys.exit(message)

    if sys.version_info.minor >= 10:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    loop.create_task(send_greetings())
    loop.create_task(worker())
    loop.create_task(executor.start_polling(dp, skip_updates=True), name='bot')
    loop.run_forever()
