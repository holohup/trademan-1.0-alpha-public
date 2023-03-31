import asyncio
from abc import ABC, abstractmethod
from decimal import Decimal

from queue_handler import QUEUE
from settings import SLEEP_PAUSE
from tinkoff.invest.utils import quotation_to_decimal
from tools.classes import Asset
from tools.get_patch_prepare_data import (async_create_sellbuy,
                                          async_get_api_data,
                                          async_patch_sellbuy,
                                          get_current_prices,
                                          get_portfolio_positions,
                                          parse_ticker_info,
                                          prepare_asset_data,
                                          prepare_assets_data)
from tools.utils import parse_ticker_int_args


async def sellbuy_cycle(asset):
    await asset.get_price_from_order_book()
    if asset.new_price != asset.last_price and asset.order_placed:
        await asset.cancel_order()
    if asset.order_id:
        await asset.update_executed()
    if not asset.order_placed and asset.next_order_amount >= asset.lot:
        await asset.place_sellbuy_order()


async def process_asset(asset):
    last_executed = asset.executed

    while asset.next_order_amount >= asset.lot:
        try:
            await sellbuy_cycle(asset)
            asset.last_price = asset.new_price
            if last_executed < asset.executed:
                await async_patch_sellbuy(asset)
                last_executed = asset.executed
            await asyncio.sleep(SLEEP_PAUSE)

        except Exception as error:
            await QUEUE.put(error)

    return (
        f'Sellbuy for {asset.ticker} finished: {asset.executed}'
        f' for {asset.avg_exec_price}'
    )


async def safe_order_cancel(asset: Asset):
    await asset.cancel_order()
    await asset.update_executed()
    if asset.executed > 0:
        await async_patch_sellbuy(asset)


class SellBuyDataProvider:
    def __init__(self, command, args) -> None:
        self._command = command
        self._args = args

    async def get_data(self):
        if self._command == 'sellbuy':
            return prepare_assets_data(await async_get_api_data('sellbuy'))
        if self._command == 'dump':
            return await PreciseDumpTicker(self._args).provide_asset_as_list()
        return await PreciseSellBuyTicker(
            self._command, self._args
        ).provide_asset_as_list()


async def sellbuy(command, args):
    assets = await SellBuyDataProvider(command, args).get_data()
    print(assets)
    if not assets:
        return 'No active assets to sell or buy'
    try:
        print(f'Starting sellbuy: {assets}')
        result = await asyncio.gather(
            *[
                asyncio.create_task(process_asset(asset), name=asset.ticker)
                for asset in assets
            ]
        )
        return f'''Покупка-продажа завершены.
         Исполнены заявки по инструментам: {result}'''

    except asyncio.CancelledError:
        await asyncio.wait(
            [asyncio.create_task(safe_order_cancel(asset)) for asset in assets]
        )
        executed_tickers = [
            f'{asset.ticker}: {asset.executed} for {asset.avg_exec_price}'
            for asset in assets
            if asset.executed > 0
        ]
        if not executed_tickers:
            executed_tickers = None
        return f'''SellBuy routine stopped.
        Already executed: {executed_tickers}.'''


class PreciseTicker(ABC):
    def __init__(self, args) -> None:
        a = parse_ticker_int_args(args)
        self._ticker, self._sum, self._amount = a.ticker, a.sum, a.amount
        self._asset = self._create_asset()

    def _create_asset(self):
        return get_current_prices(
            prepare_asset_data([self._parse_ticker_info()])
        )[0]

    def _parse_ticker_info(self):
        return parse_ticker_info(self._ticker)

    def _fill_asset_amount_and_sell(self):
        self._asset.amount = self._asset.next_order_amount = self._get_amount()
        self._asset.sell = self._need_to_sell()

    @abstractmethod
    def _get_amount(self):
        pass

    @abstractmethod
    def _need_to_sell(self):
        pass

    async def provide_asset_as_list(self):
        self._fill_asset_amount_and_sell()
        self._asset.id = await self._create_db_entry()
        return [self._asset]

    async def _create_db_entry(self) -> int:
        return await async_create_sellbuy(self._asset)


class PreciseSellBuyTicker(PreciseTicker):
    def __init__(self, command, args):
        super().__init__(args)
        self._command = command

    def _get_amount(self):
        if self._amount > 0:
            return self._amount
        price, lot = self._asset.price, self._asset.lot
        amount = (int((Decimal(self._sum) / price)) // lot) * lot
        if amount < lot:
            raise ValueError('Amount is smaller then one lot')
        return amount

    def _need_to_sell(self):
        return self._command.lower() == 'sell'


class PreciseDumpTicker(PreciseTicker):
    def __init__(self, ticker) -> None:
        super().__init__(ticker)
        self._response = get_portfolio_positions()
        self._position = 0
        self._parse_response()

    def _get_amount(self):
        return abs(self._position)

    def _need_to_sell(self):
        return self._position > 0

    def _parse_response(self):
        for position in self._response:
            if position.figi == self._asset.figi:
                self._position = int(quotation_to_decimal(position.quantity))
                return
        raise KeyError(f'{self._asset.ticker} not found in portfolio.')
