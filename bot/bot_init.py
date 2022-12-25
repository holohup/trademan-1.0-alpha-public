from aiogram import Bot, Dispatcher
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


class MyFilter(BoundFilter):
    key = 'is_me'

    def __init__(self, is_me):
        self.is_me = is_me

    async def check(self, message: Message) -> bool:
        member = await bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
        return member['user'].id == TELEGRAM_CHAT_ID


dp.filters_factory.bind(MyFilter)


async def send_message(message):
    await bot.send_message(TELEGRAM_CHAT_ID, message)
