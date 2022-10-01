from decimal import Decimal
from datetime import datetime, timezone, timedelta
from tinkoff.invest.schemas import Quotation
from tinkoff.invest.utils import decimal_to_quotation


def get_correct_price(price: float, increment: float) -> Quotation:
    answer = round(price // increment * increment, 10)
    return decimal_to_quotation(Decimal(str(answer)))

def get_lots(number_of_stocks, lot):
    return number_of_stocks // lot

def delta_minutes_to_utc(minutes):
    return datetime.now(tz=timezone.utc) + timedelta(minutes=minutes)
