from tools.utils import get_correct_price, get_lots
from tools.orders import place_long_stop, place_short_stop, cancel_order, get_assets_executed
from tools.orders import get_price_to_place_order, place_sellbuy_order
from tinkoff.invest.exceptions import RequestError
from tinkoff.invest.utils import quotation_to_decimal, decimal_to_quotation
from tinkoff.invest.schemas import OrderExecutionReportStatus
from decimal import Decimal, getcontext

getcontext().prec = 10


class Asset:
    def __init__(
            self, ticker, figi,  increment: Decimal, lot,
            price=0.0, id=0, sell=True, amount=0, executed=0, order_placed=False, order_id=None
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

    def __str__(self):
        return self.ticker

    def __repr__(self):
        return f'Asset: {self.ticker}'

    def get_correct_price(self, price):
        return get_correct_price(price, self.increment)

    def get_lots(self, number_of_stocks):
        return get_lots(number_of_stocks, self.lot)

    def place_long_stop(self, price, number_of_stocks):
        return place_long_stop(self.figi, self.get_correct_price(price), self.get_lots(number_of_stocks))

    def place_short_stop(self, price, number_of_stocks):
        return place_short_stop(self.figi, self.get_correct_price(price), self.get_lots(number_of_stocks))

    async def cancel_order(self):
        await cancel_order(self.order_id)
        self.order_placed = False

    async def get_assets_executed(self):
        return await get_assets_executed(self.order_id) * self.lot

    async def get_price_to_place_order(self):
        self.new_price = quotation_to_decimal(await get_price_to_place_order(self.figi, self.sell))

    async def place_sellbuy_order(self):

        if self.sell:
            self.price = decimal_to_quotation(self.new_price - self.increment)
        else:
            self.price = decimal_to_quotation(self.new_price + self.increment)

        r = await place_sellbuy_order(
            self.figi, self.sell, self.price, self.get_lots(self.next_order_amount)
        )

        if r.execution_report_status in [
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_NEW,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_PARTIALLYFILL,
            OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_FILL
        ]:
            self.order_placed = True
            self.order_id = r.order_id
            print(f'Поставлена заявка {self.ticker}: {self.next_order_amount} шт')
        else:
            print(f'Не удалось поставить заявку. {r}')
            self.order_placed = False
        return self.order_placed

    async def update_executed(self):
        assets_executed = await self.get_assets_executed()
        if assets_executed > 0:
            self.order_cache[self.order_id] = max(
                assets_executed,
                self.order_cache.get(self.order_id, 0)
            )
            self.executed = sum(self.order_cache.values())
            self.next_order_amount = self.amount - self.executed
            print(f'Кэш {self.ticker} . Всего исполненo: {self.executed}, кэш: {self.order_cache}')

