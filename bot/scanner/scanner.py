from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Union

from settings import CURRENT_INTEREST_RATE, TCS_RO_TOKEN
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.schemas import MoneyValue, Quotation, RealExchange
from tinkoff.invest.utils import quotation_to_decimal
from tools.get_patch_prepare_data import get_current_prices


@dataclass
class LegData:
    figi: str = ''
    ticker: str = ''
    price: Decimal = Decimal('0')
    buy_margin: Decimal = Decimal('0')


@dataclass
class StockData(LegData):
    pass


@dataclass
class FutureData(LegData):
    basic_asset_size: int = 0
    basic_asset: str = ''
    expiration_date: datetime = datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=None)
    min_price_increment_amount: Decimal = Decimal('0')
    short_enabled: bool = False
    sell_margin: Decimal = Decimal('0')
    min_price_increment: Decimal = Decimal('0')


@dataclass
class YieldingSpread:
    far_leg: FutureData
    near_leg: Union[LegData, FutureData]
    near_leg_type: str
    far_to_near_ratio: int
    margin: int = 0
    marginal_profit: float = 0


class SpreadScanner:
    def __init__(self, rate: str = '') -> None:
        if rate and not rate.isnumeric():
            raise ValueError('Rate should be a number')
        self._rate = float(rate or CURRENT_INTEREST_RATE)
        self._responses = {'shares': [], 'futures': []}
        self._spreads = []
        self._stocks, self._futures = [], []
        self._stocks_with_futures = set()
        self._futures_with_counterparts = set()

    async def scan_spreads(self):
        await self._get_instrument_lists()
        self._prefilter_instruments()
        self._filter_out_stocks_without_futures()
        self._filter_out_futures_with_no_counterparts()
        self._build_stock_and_future_lists()
        get_current_prices(self._stocks + self._futures)
        await self._get_margin_and_min_price_inc_amount()
        self._build_spreads()
        self._count_potential_profits()
        result = []
        for spread in self._spreads:
            if spread.marginal_profit > self._rate:
                result.append(
                    f'{spread.near_leg.ticker} - {spread.far_leg.ticker}: '
                    f'M = {spread.margin}, % = {spread.marginal_profit}'
                )
        print('\n'.join(result))
        return '\n'.join(result)

    def _count_potential_profits(self):
        for spread in self._spreads:
            margin, profit = ProfitCounter(spread).calculate_profit()
            spread.margin = int(margin)
            spread.marginal_profit = profit

    async def _get_instrument_lists(self):
        for instrument in self._responses.keys():
            self._responses[instrument] = await get_api_response(instrument)

    def _build_stock_and_future_lists(self):
        for instrument in self._responses['shares']:
            self._stocks.append(StockData(instrument.figi, instrument.ticker))
        for instrument in self._responses['futures']:
            if instrument.basic_asset in self._futures_with_counterparts:
                self._futures.append(
                    FutureData(
                        instrument.figi,
                        instrument.ticker,
                        basic_asset=instrument.basic_asset,
                        expiration_date=instrument.expiration_date,
                        short_enabled=instrument.short_enabled_flag,
                        basic_asset_size=int(
                            quotation_to_decimal(instrument.basic_asset_size)
                        ),
                        min_price_increment=quotation_to_decimal(
                            instrument.min_price_increment
                        )
                    )
                )

    def _build_spreads(self):
        self._build_spreads_from_stocks()
        self._build_spreads_from_futures()

    def _build_spreads_from_stocks(self):
        for stock in self._stocks:
            for future in self._futures:
                if stock.ticker == future.basic_asset:
                    self._spreads.append(
                        YieldingSpread(
                            far_leg=future,
                            near_leg=stock,
                            near_leg_type='S',
                            far_to_near_ratio=future.basic_asset_size,
                        )
                    )

    def _build_spreads_from_futures(self):
        for near_future in self._futures:
            for far_future in self._futures:
                if self._leg_combination_not_good(far_future, near_future):
                    continue
                self._spreads.append(
                    YieldingSpread(
                        far_leg=far_future,
                        near_leg=near_future,
                        near_leg_type='F',
                        far_to_near_ratio=1,
                    )
                )

    def _leg_combination_not_good(self, far_future, near_future):
        return (
            near_future is far_future
            or near_future.basic_asset != far_future.basic_asset
            or near_future.expiration_date > far_future.expiration_date
            or near_future.price >= far_future.price
            or near_future.price == Decimal('0')
            or far_future.price == Decimal('0')
            or far_future.short_enabled is False
            or far_future.ticker[:2] != near_future.ticker[:2]
        )

    def _prefilter_instruments(self):
        for inst_type in self._responses.keys():
            self._responses[inst_type] = ResponseFilter(
                self._responses[inst_type]
            ).filter_instruments()

    def _filter_out_stocks_without_futures(self):
        all_stock_tickers = set()
        for instrument in self._responses['shares']:
            all_stock_tickers.add(instrument.ticker)
        for instrument in self._responses['futures']:
            basic_asset = instrument.basic_asset
            if (
                basic_asset in all_stock_tickers
                and basic_asset not in self._stocks_with_futures
            ):
                self._stocks_with_futures.add(basic_asset)

    def _filter_out_futures_with_no_counterparts(self):
        counter = {ticker: 1 for ticker in self._stocks_with_futures}
        for instrument in self._responses['futures']:
            ticker = instrument.basic_asset
            if ticker not in counter:
                counter[ticker] = 0
            counter[ticker] += 1
        for ticker, count in counter.items():
            if count > 1:
                self._futures_with_counterparts.add(ticker)

    async def _get_margin_and_min_price_inc_amount(self):
        for instrument in self._stocks:
            instrument.buy_margin = self._get_instrument_price(instrument)

        for instrument in self._futures:
            response = await get_margin_response(instrument.figi)
            instrument.buy_margin = quotation_to_decimal(
                self._mv_to_q(response.initial_margin_on_buy)
            )
            instrument.sell_margin = quotation_to_decimal(
                self._mv_to_q(response.initial_margin_on_sell)
            )
            instrument.min_price_increment_amount = quotation_to_decimal(
                response.min_price_increment_amount
            )
            instrument.price = self._get_instrument_price(instrument)

    def _mv_to_q(self, mv: MoneyValue):
        return Quotation(units=mv.units, nano=mv.nano)

    def _get_instrument_price(self, instrument):
        if isinstance(instrument, StockData):
            return instrument.price
        return (
            instrument.price
            / instrument.min_price_increment
            * instrument.min_price_increment_amount
        )


async def scan(command, args):
    scanner = SpreadScanner(args)
    return await scanner.scan_spreads()


class ResponseFilter:
    def __init__(self, response):
        self._response = response
        self._validate_response()
        self._instruments = response.instruments

    def _validate_response(self):
        if not hasattr(self._response, 'instruments'):
            raise KeyError(f'No instruments in response: {self._response}')
        if not isinstance(self._response.instruments, list):
            raise ValueError(
                'Response doesn not contain a list of instruments: '
                f'{self._response}'
            )
        if self._response.instruments == []:
            raise ValueError(f'Empty response list: {self._response}')

    def filter_instruments(self):
        self._instruments = self._apply_basic_filter()
        return self._instruments

    def _apply_basic_filter(self):
        filtered_instruments = []
        for instrument in self._instruments:
            if self._basic_filter(instrument):
                filtered_instruments.append(instrument)
        return filtered_instruments

    def _basic_filter(self, instrument):
        return all(
            (
                instrument.real_exchange == RealExchange.REAL_EXCHANGE_MOEX,
                quotation_to_decimal(instrument.min_price_increment)
                > Decimal('0'),
                instrument.api_trade_available_flag is True,
                instrument.buy_available_flag is True
                and instrument.sell_available_flag is True,
                not hasattr(instrument, 'last_trade_date')
                or instrument.last_trade_date > datetime.now(tz=timezone.utc),
            )
        )


class ProfitCounter:
    def __init__(self, spread: YieldingSpread) -> None:
        self._far_leg = spread.far_leg
        self._near_leg = spread.near_leg
        self._ratio = spread.far_to_near_ratio
        self._nl_type = spread.near_leg_type
        self._spread = spread

    def calculate_profit(self):
        absolute_profit = self._total_profit / self._total_margin
        year_periods = 365 / self._days_till_profit
        year_adjusted_profit = float((1 + absolute_profit)) ** year_periods - 1
        return self._total_margin, year_adjusted_profit * 100

    @property
    def _days_till_profit(self):
        return (
            self._far_leg.expiration_date - datetime.now(tz=timezone.utc)
        ).days

    @property
    def _total_margin(self):
        return (
            self._near_leg.buy_margin * self._ratio + self._far_leg.sell_margin
        )

    @property
    def _total_profit(self):
        return self._far_leg.price - self._ratio * self._near_leg.price


async def get_margin_response(figi: str):
    async with AsyncRetryingClient(
        TCS_RO_TOKEN,
        RetryClientSettings(use_retry=True, max_retry_attempt=10),
    ) as client:
        return await client.instruments.get_futures_margin(figi=figi)


async def get_api_response(instrument: str):
    async with AsyncRetryingClient(
        TCS_RO_TOKEN,
        RetryClientSettings(use_retry=True, max_retry_attempt=10),
    ) as client:
        return await getattr(client.instruments, instrument)()
