from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from tinkoff.invest.schemas import Quotation
from tinkoff.invest.utils import decimal_to_quotation


@dataclass
class SellBuyCommand:
    ticker: str
    amount: int = 0
    sum: int = 0


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


def parse_ticker_int_args(args: str) -> SellBuyCommand:
    sum, amount = 0, 0
    arguments = args.split()
    if len(arguments) == 1:
        return SellBuyCommand(arguments[0], amount, sum)
    if len(arguments) > 2:
        raise ValueError('Too many arguments, aborting')
    if arguments[0].isnumeric():
        ticker = arguments[1]
        amount = int(arguments[0])
    elif arguments[1].isnumeric():
        ticker = arguments[0]
        sum = int(arguments[1])
    else:
        raise ValueError(
            'Format for arguments is: <ticker> <sum> or <amount> <ticker>'
        )
    return SellBuyCommand(ticker, amount, sum)
