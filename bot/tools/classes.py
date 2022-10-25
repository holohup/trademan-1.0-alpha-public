from decimal import Decimal, getcontext

import tinkoff.invest
from tinkoff.invest.schemas import OrderExecutionReportStatus
from tinkoff.invest.utils import quotation_to_decimal, decimal_to_quotation
from tools.orders import get_price_to_place_order, place_sellbuy_order, get_closest_execution_price
from tools.orders import perform_market_trade
from tools.orders import place_long_stop, place_short_stop, cancel_order, get_execution_report
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
        self.order_cache = {}
        self.next_order_amount = amount
        self.new_price = Decimal(0)
        self.last_price = Decimal(0)
        self.closest_execution_price = Decimal(0)
        self.orders_average_price = Decimal(0)
        self.orders_prices_cache = {}
        if executed and executed > 0:
            self.order_cache['initial'] = executed
            self.next_order_amount = amount - executed

    def __str__(self):
        return self.ticker

    def __repr__(self):
        return f'Asset: {self.ticker}'

    def get_correct_price(self, price):
        return get_correct_price(price, self.increment)

    def get_lots(self, number_of_stocks):
        return get_lots(number_of_stocks, self.lot)

    def place_long_stop(self, price, number_of_stocks):
        return place_long_stop(
            self.figi,
            self.get_correct_price(price),
            self.get_lots(number_of_stocks),
        )

    def place_short_stop(self, price, number_of_stocks):
        return place_short_stop(
            self.figi,
            self.get_correct_price(price),
            self.get_lots(number_of_stocks),
        )

    async def cancel_order(self):
        await cancel_order(self.order_id)
        print(f'{self.ticker} order cancelled.')

    async def get_assets_executed(self):
        return await get_execution_report(self.order_id)

    async def get_price_to_place_order(self):
        self.new_price = quotation_to_decimal(
            await get_price_to_place_order(self.figi, self.sell)
        )

    async def get_closest_execution_price(self):
        self.closest_execution_price = quotation_to_decimal(
            await get_closest_execution_price(self.figi, self.sell)
        )

    def parse_order_response(self, response: tinkoff.invest.PostOrderResponse):
        self.order_id = response.order_id
        if response.execution_report_status in [
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_UNSPECIFIED,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_REJECTED,
        ]:
            print(f'Заяка не активна и не отменена мной. {response}')
            self.order_placed = False
            print(response.execution_report_status)
            return

        # if response.execution_report_status == OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_CANCELLED:
        #     self.order_placed = False
        # else:
        self.order_placed = True

        if response.lots_executed == 0:
            return

        self.order_cache[self.order_id] = max(
            response.lots_executed * self.lot, self.order_cache.get(self.order_id, 0)
        )
        self.executed = sum(self.order_cache.values())
        executed_without_initial = self.executed - self.order_cache.get('initial', 0)
        self.orders_prices_cache[self.order_id] = quotation_to_decimal(response.executed_order_price)
        total_executed_price = 0
        for order_id, amount in self.order_cache.items():
            total_executed_price += amount * self.orders_prices_cache[order_id] if order_id != 'initial' else 0
        self.orders_average_price = total_executed_price / Decimal(executed_without_initial)
        self.next_order_amount = self.amount - self.executed
        sell = 'Sell' if self.sell else 'Buy'
        print(
            f'parse_order_response: Заявка {sell} {self.next_order_amount} {self.ticker}: '
            f'{response.lots_executed} лот., Кэш: {self.order_cache}. Executed without initial: '
            f'{executed_without_initial}, Prices cache: {self.orders_prices_cache}, '
            f'average price without initial: {self.orders_average_price}, next_order_amount: '
            f'{self.next_order_amount}, total_executed_price = {total_executed_price}'
        )

    def parse_order_status(self, response: tinkoff.invest.OrderState):
        # self.order_id = response.order_id
        # if response.execution_report_status in [
        #     OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_UNSPECIFIED,
        #     OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_REJECTED,
        # ]:
        #     print(f'Заяка не активна и не отменена мной. {response}')
        #     self.order_placed = False
        #     print(response.execution_report_status)
        #     return

        if response.execution_report_status == OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_CANCELLED:
            self.order_placed = False
        # else:
        #     self.order_placed = True

        if response.lots_executed == 0:
            return

        self.order_cache[self.order_id] = max(
            response.lots_executed * self.lot, self.order_cache.get(self.order_id, 0)
        )
        self.executed = sum(self.order_cache.values())
        executed_without_initial = self.executed - self.order_cache.get('initial', 0)
        self.orders_prices_cache[self.order_id] = quotation_to_decimal(response.average_position_price)
        total_executed_price = 0
        for order_id, amount in self.order_cache.items():
            total_executed_price += amount * self.orders_prices_cache[order_id] if order_id != 'initial' else 0
        self.orders_average_price = total_executed_price / Decimal(executed_without_initial)
        self.next_order_amount = self.amount - self.executed
        sell = 'Sell' if self.sell else 'Buy'
        print(
            f'parse_order_status: Заявка {sell} {self.next_order_amount} {self.ticker}: '
            f'{response.lots_executed} лот., Кэш: {self.order_cache}. Executed without initial: '
            f'{executed_without_initial}, Prices cache: {self.orders_prices_cache}, '
            f'average price without initial: {self.orders_average_price}, next_order_amount: '
            f'{self.next_order_amount}, total_executed_price = {total_executed_price}'
        )

    async def perform_market_trade(self):
        r = await perform_market_trade(
            self.figi, self.sell, self.get_lots(self.next_order_amount)
        )
        self.parse_order_response(r)

    async def place_sellbuy_order(self):

        self.price = decimal_to_quotation(self.new_price)
        # if self.sell:
        #     self.price = decimal_to_quotation(self.new_price - self.increment)
        # else:
        #     self.price = decimal_to_quotation(self.new_price + self.increment)

        r = await place_sellbuy_order(
            self.figi,
            self.sell,
            self.price,
            self.get_lots(self.next_order_amount),
        )
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
            exec_price: Decimal(0)
    ):
        self.far_leg = far_leg
        self.near_leg = near_leg
        self.sell = sell
        self.price = price
        self.id = id
        self.amount = amount
        self.avg_execution_price = exec_price
        self.executed = executed
        self.near_leg_type = near_leg_type
        self.base_asset_amount = base_asset_amount
        self.ratio = (
            base_asset_amount if self.near_leg_type == 'S' else 1
        )  # stocks in far leg / stocks in near leg

    def __str__(self):
        direction = 'Sell' if self.sell else 'Buy'
        return f'{direction} {self.amount} {self.near_leg.ticker} - {self.far_leg.ticker} for {self.price}'

    def __repr__(self):
        direction = 'Sell' if self.sell else 'Buy'
        return (
            f'\n {direction} [{self.executed}/{self.amount}] '
            f'{self.near_leg_type} {self.near_leg.ticker} - '
            f'F {self.far_leg.ticker} for {self.price} avg={self.avg_execution_price}'
        )

    async def even_execution(self):
        if not self.far_leg.executed * self.ratio > self.near_leg.executed:
            return
        self.near_leg.next_order_amount = (self.far_leg.executed * self.ratio - self.near_leg.executed)
        await self.near_leg.perform_market_trade()

        far_leg_avg_price = self.far_leg.orders_average_price
        near_leg_avg_price = self.near_leg.orders_average_price * Decimal(self.ratio)
        session_orders_execution_price = far_leg_avg_price - near_leg_avg_price
        executed_without_initial = self.far_leg.executed - self.far_leg.order_cache.get('initial', 0)
        total_execution_price = float(
            session_orders_execution_price) * executed_without_initial + self.avg_execution_price * self.executed
        self.executed = self.far_leg.executed

        self.avg_execution_price = total_execution_price / self.executed
        print(f'even_execution: {far_leg_avg_price}, {near_leg_avg_price}, {session_orders_execution_price},'
              f' {self.avg_execution_price}, {self.executed}, {total_execution_price},'
              f'{self.executed}, {self.avg_execution_price}, {executed_without_initial}')


if __name__ == '__main__':
    pass
