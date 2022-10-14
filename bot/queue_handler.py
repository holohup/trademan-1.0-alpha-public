import asyncio
from bot_init import bot, TELEGRAM_CHAT_ID

QUEUE = asyncio.Queue()


async def worker():
    while True:
        message = await QUEUE.get()
        if message:
            await bot.send_message(TELEGRAM_CHAT_ID, message)
            QUEUE.task_done()
        await asyncio.sleep(1)
