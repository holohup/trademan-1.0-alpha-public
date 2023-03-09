from decimal import Decimal, getcontext
from typing import NamedTuple

import tinkoff.invest
from tinkoff.invest.schemas import OrderExecutionReportStatus
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal
from tools.cache import OrdersCache
from tools.orders import (cancel_order, get_execution_report,
                          get_price_from_order_book, place_order)
from tools.utils import get_correct_price, get_lots

from .trading_time import TradingTime

getcontext().prec = 10


class Asset:
    def __init__(
        self,
        ticker,
        figi,
        min_price_increment: Decimal,
        lot,
        price=Decimal(0.0),
        id=0,
        sell=True,
        amount=0,
        executed=0,
        avg_exec_price=Decimal('0'),
        order_placed=False,
        order_id=None,
        morning_trading=False,
        evening_trading=False,
        asset_type='S',
    ):
        self.ticker = ticker
        self.figi = figi
        self.min_price_increment = Decimal(min_price_increment)
        self.lot = lot
        self.price = Decimal(price)
        self.id = id
        self.sell = sell
        self.amount = amount
        self.order_placed = order_placed
        self.order_id = order_id
        self.new_price = Decimal(0)
        self.last_price = Decimal(0)
        self.morning_trading = morning_trading
        self.evening_trading = evening_trading
        self.asset_type = asset_type
        if executed and executed > 0:
            self.order_cache = OrdersCache(executed, avg_exec_price)
            self.next_order_amount = amount - executed
        else:
            self.order_cache = OrdersCache()
            self.next_order_amount = amount

    def __str__(self):
        return self.ticker

    def __repr__(self):
        return f'Asset: {self.ticker}'

    def get_correct_price(self, price):
        return get_correct_price(price, self.min_price_increment)

    def get_lots(self, number_of_stocks):
        return get_lots(number_of_stocks, self.lot)

    async def cancel_order(self):
        await cancel_order(self.order_id)

    async def get_assets_executed(self):
        return await get_execution_report(self.order_id)

    async def get_price_from_order_book(self):
        self.new_price = quotation_to_decimal(
            await get_price_from_order_book(self)
        )

    def _update_upon_execution(self, response, price):
        if (
            response.lots_executed == 0
            or self.order_cache.executed_by_id(self.order_id)
            >= response.lots_executed * self.lot
        ):
            return

        self.order_cache.update(
            self.order_id,
            response.lots_executed * self.lot,
            quotation_to_decimal(price),
        )
        self.next_order_amount = self.amount - self.executed

    def parse_order_response(self, response: tinkoff.invest.PostOrderResponse):
        self.order_id = response.order_id
        if self._new_order_is_rejected(response):
            self.order_placed = False
            return
        self.order_placed = True
        self._update_upon_execution(response, response.executed_order_price)

    def parse_order_status(self, response: tinkoff.invest.OrderState):
        self._update_order_placed(response)
        self._update_upon_execution(response, response.average_position_price)

    def _update_order_placed(self, response):
        self.order_placed = response.execution_report_status not in (
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_CANCELLED,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL,
        )

    def _new_order_is_rejected(self, response):
        return response.execution_report_status in (
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_UNSPECIFIED,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_REJECTED,
        )

    async def perform_market_trade(self):
        r = await place_order(self, 'market')
        self.parse_order_response(r)

    async def place_sellbuy_order(self):
        self.price = decimal_to_quotation(self.new_price)
        r = await place_order(self, 'limit')
        self.parse_order_response(r)

    async def update_executed(self):
        r = await self.get_assets_executed()
        self.parse_order_status(r)

    @property
    def latest_order_price(self):
        return self.order_cache.price_by_id(self.order_id)

    @property
    def executed(self):
        return self.order_cache.amount

    @property
    def avg_exec_price(self):
        return self.order_cache.avg_price

    @property
    def is_trading_now(self):
        return TradingTime(self).is_trading_now

    @property
    def seconds_till_trading_starts(self):
        return TradingTime(self).seconds_till_trading_starts


class Spread:
    def __init__(
        self,
        far_leg: Asset,
        near_leg: Asset,
        sell: bool,
        price: int,
        id: int,
        ratio: int,
        amount: int,
    ):
        self.far_leg = far_leg
        self.near_leg = near_leg
        self.sell = sell
        self.price = price
        self.id = id
        self.ratio = ratio
        self.amount = amount

    async def even_execution(self):
        if self._near_leg_next_order_amount <= 0:
            return
        await self._perform_near_leg_market_trade()

    async def _perform_near_leg_market_trade(self):
        self.near_leg.next_order_amount = self._near_leg_next_order_amount
        await self.near_leg.perform_market_trade()

    @property
    def executed(self):
        return self.far_leg.order_cache.amount

    @property
    def avg_execution_price(self) -> Decimal:
        if self.executed == 0:
            return Decimal('0')
        return (
            Decimal(self.far_leg.avg_exec_price * self.far_leg.executed)
            - Decimal(self.near_leg.avg_exec_price * self.near_leg.executed)
        ) / (self.executed)

    @property
    def _near_leg_next_order_amount(self):
        return self.far_leg.executed * self.ratio - self.near_leg.executed

    @property
    def _trade_direction(self):
        return 'Sell' if self.sell else 'Buy'

    @property
    def is_trading_now(self):
        return all((self.far_leg.is_trading_now, self.near_leg.is_trading_now))

    @property
    def seconds_till_trading_starts(self):
        return max(
            self.far_leg.seconds_till_trading_starts,
            self.near_leg.seconds_till_trading_starts,
        )

    def __str__(self):
        return (
            f'{self._trade_direction} {self.amount} {self.far_leg.ticker}'
            f' - {self.near_leg.ticker} for {self.price}'
        )

    def __repr__(self):
        return (
            f'\n {self._trade_direction} [{self.executed}/{self.amount}]'
            f' {self.far_leg.ticker} - {self.near_leg.ticker}'
            f' for {self.price} avg={self.avg_execution_price}'
        )


class StopOrderParams(NamedTuple):
    direction: str
    stop_type: str
    expiration: str


class StopOrder(NamedTuple):
    asset: Asset
    price: Decimal
    sum: int
    params: StopOrderParams
