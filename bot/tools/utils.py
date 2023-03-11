from datetime import datetime, timedelta, timezone
from decimal import Decimal

from tinkoff.invest.schemas import Quotation
from tinkoff.invest.utils import decimal_to_quotation


def get_correct_price(price: Decimal, increment: Decimal) -> Quotation:
    if not isinstance(price, Decimal) or not isinstance(increment, Decimal):
        raise ValueError('Price and Increment should be Decimal.')
    if price <= 0 or increment <= 0:
        raise ValueError('Price and Increment should be positive.')
    answer = price // increment * increment
    return decimal_to_quotation(answer)


def get_lots(number_of_stocks, lot):
    return number_of_stocks // lot


def delta_minutes_to_utc(minutes):
    return datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)
