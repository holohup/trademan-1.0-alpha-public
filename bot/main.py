import logging
from aiogram import executor
from bot_init import dp
import commands


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)


