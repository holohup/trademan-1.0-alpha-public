from telegram import Update, Bot
from telegram.ext import Updater, CallbackContext, Filters, MessageHandler, CommandHandler
from settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import place_stops
import cancel_all_orders

def log_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            message = f'Ошибка: {error}'
            print(message)
            raise error
    return wrapper

@bot.message_handler(commands=['start', 'hello'])
def help_handler(update: Update, context: CallbackContext):
    message = 'hello!'
    update.message.reply_text(message)

def place_l_stops(update: Update, context: CallbackContext):
    update.message.reply_text('placing stops')
    message = place_stops.place_long_stops()
    update.message.reply_text(message)


def place_s_stops(update: Update, context: CallbackContext):
    update.message.reply_text('placing short stops')
    message = place_stops.place_short_stops()
    update.message.reply_text(message)


def cancel_orders(update: Update, context: CallbackContext):
    update.message.reply_text('cancelling all orders')
    message = cancel_all_orders.cancel_orders()
    update.message.reply_text(message)


def stop(update: Update, context: CallbackContext):
    update.message.reply_text('stopping')



bot = Bot(token=TELEGRAM_TOKEN)
filters = Filters.user(user_id=int(TELEGRAM_CHAT_ID))
updater = Updater(bot=bot)
start_handler = CommandHandler('start', help_handler, filters)
stops_handler = CommandHandler('stops', place_l_stops, filters)
shorts_handler = CommandHandler('shorts', place_s_stops, filters)
cancel_handler = CommandHandler('cancel', cancel_orders, filters)
updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(stops_handler)
updater.dispatcher.add_handler(shorts_handler)
updater.dispatcher.add_handler(cancel_handler)
updater.start_polling(drop_pending_updates=True)
updater.idle()
