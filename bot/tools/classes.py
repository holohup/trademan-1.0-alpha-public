from decimal import Decimal, getcontext
from typing import NamedTuple

import tinkoff.invest
from tinkoff.invest.schemas import OrderExecutionReportStatus
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal
from tools.cache import OrdersCache
from tools.orders import (cancel_order, get_execution_report,
                          get_price_from_order_book, place_order)
from tools.utils import get_correct_price, get_lots

getcontext().prec = 10


class Asset:
    def __init__(
        self,
        ticker,
        figi,
        increment: Decimal,
        lot,
        price=0.0,
        id=0,
        sell=True,
        amount=0,
        executed=0,
        order_placed=False,
        order_id=None,
    ):
        self.ticker = ticker
        self.figi = figi
        self.increment = Decimal(increment)
        self.lot = lot
        self.price = Decimal(price)
        self.id = id
        self.sell = sell
        self.amount = amount
        self.executed = executed
        self.order_placed = order_placed
        self.order_id = order_id
        self.new_price = Decimal(0)
        self.last_price = Decimal(0)
        if executed and executed > 0:
            self.order_cache = OrdersCache(executed, Decimal(0))
            self.next_order_amount = amount - executed
        else:
            self.order_cache = OrdersCache()
            self.next_order_amount = amount

    def __str__(self):
        return self.ticker

    def __repr__(self):
        return f'Asset: {self.ticker}'

    def get_correct_price(self, price):
        return get_correct_price(price, self.increment)

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
        self.executed = self.order_cache.amount
        self.orders_average_price, _ = self.order_cache.session_avg_and_amount
        self.next_order_amount = self.amount - self.executed

    def parse_order_response(self, response: tinkoff.invest.PostOrderResponse):
        self.order_id = response.order_id
        if response.execution_report_status in [
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_UNSPECIFIED,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_REJECTED,
        ]:
            self.order_placed = False
            return
        self.order_placed = True

        self._update_upon_execution(response, response.executed_order_price)

    def parse_order_status(self, response: tinkoff.invest.OrderState):
        if (
            response.execution_report_status
            == OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_CANCELLED
        ):
            self.order_placed = False

        self._update_upon_execution(response, response.average_position_price)

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


class Spread:
    def __init__(
        self,
        far_leg: Asset,
        near_leg: Asset,
        sell: bool,
        price: int,
        id: int,
        amount: int,
        executed: int,
        near_leg_type: str,
        base_asset_amount: int,
        exec_price: Decimal,
    ):
        self.far_leg = far_leg
        self.near_leg = near_leg
        self.sell = sell
        self.price = price
        self.id = id
        self.amount = amount
        self.avg_execution_price = Decimal('0')
        self.executed = executed
        self.near_leg_type = near_leg_type
        self.base_asset_amount = base_asset_amount
        self.ratio = (
            base_asset_amount if self.near_leg_type == 'S' else 1
        )  # stocks in far leg / stocks in near leg
        if executed and executed > 0:
            self.cache = OrdersCache(executed, exec_price)
        else:
            self.cache = OrdersCache()

    def __str__(self):
        direction = 'Sell' if self.sell else 'Buy'
        return (
            f'{direction} {self.amount} {self.near_leg.ticker}'
            f' - {self.far_leg.ticker} for {self.price}'
        )

    def __repr__(self):
        direction = 'Sell' if self.sell else 'Buy'
        return f'''\n {direction} [{self.executed}/{self.amount}]
             {self.near_leg_type} {self.near_leg.ticker} -
             F {self.far_leg.ticker} for {self.price}
             avg={self.avg_execution_price}'''

    async def perform_near_leg_market_trade(self, amount):
        self.near_leg.next_order_amount = amount
        await self.near_leg.perform_market_trade()

    def update_cache(self):
        order_id = self.far_leg.order_id
        far_leg_price = self.far_leg.order_cache.price_by_id(order_id)
        near_leg_price = (
            self.near_leg.order_cache.price_by_id(self.near_leg.order_id)
            * self.ratio
        )
        self.cache.update(
            order_id,
            self.far_leg.order_cache.executed_by_id(order_id),
            far_leg_price - near_leg_price,
        )

    async def even_execution(self):
        near_leg_equivalent = self.far_leg.executed * self.ratio
        if near_leg_equivalent <= self.near_leg.executed:
            return
        await self.perform_near_leg_market_trade(
            near_leg_equivalent - self.near_leg.executed
        )
        self.update_cache()

        self.executed = self.cache.amount
        self.avg_execution_price = self.cache.avg_price


class StopOrderParams(NamedTuple):
    direction: str
    stop_type: str
    expiration: str


class StopOrder(NamedTuple):
    asset: Asset
    price: Decimal
    sum: int
    params: StopOrderParams
