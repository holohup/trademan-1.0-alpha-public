from decimal import Decimal
from datetime import datetime, timezone, timedelta
from tinkoff.invest.schemas import Quotation
from tinkoff.invest.utils import decimal_to_quotation
import requests
from settings import TELEGRAM_TOKEN


def check_for_stop() -> bool:
    updates_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates'
    response = requests.get(updates_url).json()['result']
    if response:
        response = response[-1]['message']['text']
        if response.lower() == 'stop':
            return True
    return False


def get_correct_price(price: float, increment: float) -> Quotation:
    answer = round(price // increment * increment, 10)
    return decimal_to_quotation(Decimal(str(answer)))

def get_lots(number_of_stocks, lot):
    return number_of_stocks // lot

def delta_minutes_to_utc(minutes):
    return datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)
