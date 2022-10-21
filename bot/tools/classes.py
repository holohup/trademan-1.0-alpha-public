from decimal import Decimal, getcontext

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
        self.last_order_execution_price = Decimal(0)
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
        self.order_placed = False

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

    async def perform_market_trade(self):
        r = await perform_market_trade(
            self.figi, self.sell, self.get_lots(self.next_order_amount)
        )

        if r.execution_report_status in [
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_NEW,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_PARTIALLYFILL,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL,
        ]:
            self.order_id = r.order_id
            self.last_order_execution_price = quotation_to_decimal(r.total_order_amount)
            self.order_placed = False


            print(
                f'Исполнена заявка {self.ticker}: {self.next_order_amount} шт, Кэш {self.ticker}: {self.order_cache}'
            )
        else:
            print(f'Не удалось поставить заявку. {r}')
            self.order_placed = False
        return self.order_placed

    async def place_sellbuy_order(self):

        if self.sell:
            # self.price = decimal_to_quotation(self.new_price - self.increment)
            self.price = decimal_to_quotation(self.new_price)
        else:
            # self.price = decimal_to_quotation(self.new_price + self.increment)
            self.price = decimal_to_quotation(self.new_price)

        r = await place_sellbuy_order(
            self.figi,
            self.sell,
            self.price,
            self.get_lots(self.next_order_amount),
        )

        if r.execution_report_status in [
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_NEW,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_PARTIALLYFILL,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL,
        ]:
            self.order_placed = True
            self.order_id = r.order_id
            # print(f'Поставлена заявка {self.ticker}: {self.next_order_amount} шт')
        else:
            print(f'Не удалось поставить заявку. {r}')
            self.order_placed = False
        return self.order_placed

    async def update_executed(self):
        execution_report = await self.get_assets_executed()
        if execution_report.lots_executed > 0:
            self.order_cache[self.order_id] = max(
                execution_report.lots_executed * self.lot, self.order_cache.get(self.order_id, 0)
            )
            self.executed = sum(self.order_cache.values())
            self.last_order_execution_price = (quotation_to_decimal(execution_report.executed_order_price))
            self.next_order_amount = self.amount - self.executed
            #
            # print(
            #     f'Кэш {self.ticker} . Всего исполненo: {self.executed}, '
            #     f'кэш: {self.order_cache}, next order amount: {self.next_order_amount}, '
            #     f'at sum price:{self.last_order_execution_price}'
            # )


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
        if self.near_leg.order_id:
            await self.near_leg.update_executed()
        if self.far_leg.executed * self.ratio > self.near_leg.executed:
            self.near_leg.next_order_amount = (
                    self.far_leg.executed * self.ratio - self.near_leg.executed
            )
            await self.near_leg.perform_market_trade()
            await self.near_leg.update_executed()

            last_orders_execution_price = float(
                    self.far_leg.last_order_execution_price - self.near_leg.last_order_execution_price
            )
            total_execution_price = last_orders_execution_price + self.avg_execution_price * self.executed
            self.executed = self.far_leg.executed
            self.avg_execution_price = total_execution_price / self.executed


if __name__ == '__main__':
    pass
