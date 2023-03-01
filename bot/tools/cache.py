from decimal import Decimal
from typing import NamedTuple


class CachedItem(NamedTuple):
    amount: int
    price: Decimal


class OrdersCache:
    def __init__(self, amount=0, price=Decimal(0)) -> None:
        self._validate_data(order_id='', amount=amount, price=price)
        self._orders = {}
        self._amount = amount
        self._average_price = price
        if amount > 0:
            self.update('initial', amount, price)

    @property
    def items(self):
        return self._orders

    def _validate_data(self, order_id, amount, price):
        if not isinstance(order_id, str):
            raise ValueError('Order id should be a str')
        if not isinstance(price, Decimal):
            raise ValueError('Cache price should be a Decimal')
        if not isinstance(amount, int):
            raise ValueError('Cache amount should be an integer')
        if amount < 0:
            raise ValueError('Amount should not be a negative number')

    def update(self, order_id, amount, price):
        self._validate_data(order_id, amount, price)
        self._orders[order_id] = CachedItem(amount, price)
        self._average_price, self._amount = self._count_avg_price_and_amount()

    def _count_avg_price_and_amount(self):
        if not self._orders:
            return Decimal('0'), 0
        sum, amount = 0, 0
        for item in self._orders.values():
            sum += item.price * item.amount
            amount += item.amount
        return sum / amount, amount

    @property
    def amount(self):
        return self._amount

    @property
    def avg_price(self):
        return self._average_price

    def executed_by_id(self, order_id):
        if order_id in self._orders:
            return self._orders[order_id].amount
        return 0
