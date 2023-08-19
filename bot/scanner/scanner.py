from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import NamedTuple, Union

from settings import CURRENT_INTEREST_RATE, TCS_RO_TOKEN
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.schemas import MoneyValue, Quotation, RealExchange
from tinkoff.invest.utils import quotation_to_decimal
from tools.get_patch_prepare_data import (get_current_prices,
                                          get_current_prices_by_uid)


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
    delta: int = 0
    days: int = 0


class DividendSpread(NamedTuple):
    stock_ticker: str
    future_ticker: str
    dividend: float
    days_till_expiration: int
    yld: float


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
        for spread in sorted(
            self._spreads, key=lambda x: x.marginal_profit, reverse=True
        ):
            if spread.marginal_profit > self._rate:
                result.append(
                    f'{spread.near_leg.ticker} - {spread.far_leg.ticker}: '
                    f'M = {spread.margin}, %={spread.marginal_profit} '
                    f'delta = {spread.delta}, {spread.days} days.'
                )
        if len(result) > 70:
            result = result[:70]
        return '\n'.join(result) if result else 'No matching spreads found.'

    def _count_potential_profits(self):
        for spread in self._spreads:
            margin, profit, delta, days = ProfitCounter(
                spread
            ).calculate_profit()
            spread.margin = int(margin)
            spread.marginal_profit = profit
            spread.delta = int(delta)
            spread.days = days

    async def _get_instrument_lists(self):
        for instrument in self._responses.keys():
            self._responses[instrument] = await get_api_response(instrument)

    def _build_stock_and_future_lists(self):
        for instrument in self._responses['shares']:
            self._stocks.append(StockData(instrument.figi, instrument.ticker))
        for instrument in self._responses['futures']:
            if instrument.basic_asset in self._futures_with_counterparts and (
                instrument.asset_type
                == 'TYPE_SECURITY'
                # or instrument.asset_type == 'TYPE_COMMODITY'
            ):
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
                        ),
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
        return (
            self._total_margin,
            round(year_adjusted_profit * 100, 2),
            self._total_profit,
            self._days_till_profit,
        )

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


async def dividend_scan():
    max_futures_ahead = 3
    interest_rate = 12
    percent_threshold = 1
    shares = await get_api_response('shares')
    shares = shares.instruments
    filtered_shares = {
        share.ticker: share
        for share in shares
        if share.api_trade_available_flag is True
        and share.sell_available_flag is True
        and quotation_to_decimal(share.min_price_increment) > Decimal('0')
        and share.short_enabled_flag is True
    }
    futures = await get_api_response('futures')
    futures = futures.instruments
    filtered_futures = {}
    for future in futures:
        if (
            future.api_trade_available_flag is False
            or future.buy_available_flag is False
            or quotation_to_decimal(future.min_price_increment) <= Decimal('0')
            or future.basic_asset not in filtered_shares.keys()
            or future.last_trade_date <= datetime.now(tz=timezone.utc)
        ):
            continue
        if future.basic_asset not in filtered_futures:
            filtered_futures[future.basic_asset] = []
        filtered_futures[future.basic_asset].append(future)

    for stock_ticker in filtered_futures:
        filtered_futures[stock_ticker] = sorted(
            filtered_futures[stock_ticker], key=lambda d: d.expiration_date
        )[:max_futures_ahead]
    filtered_shares = {
        ticker: uid
        for ticker, uid in filtered_shares.items()
        if ticker in filtered_futures.keys()
    }
    share_prices = get_current_prices_by_uid(list(filtered_shares.values()))
    future_prices = get_current_prices_by_uid(
        [d for f in filtered_futures.values() for d in f]
    )
    result = []
    for ticker in filtered_shares:
        price = share_prices[filtered_shares[ticker].uid]
        for future in filtered_futures[ticker]:
            f_price = future_prices[future.uid]
            days_till_expiration = (
                future.expiration_date - datetime.now(tz=timezone.utc)
            ).days
            honest_stock_price = (
                price
                * quotation_to_decimal(future.basic_asset_size)
                * (
                    (1 + Decimal(interest_rate / 100))
                    ** Decimal((days_till_expiration / 365))
                )
            )
            delta = f_price - honest_stock_price
            if delta < 0:
                norm_delta = -delta / quotation_to_decimal(
                    future.basic_asset_size
                )
                result.append(
                    DividendSpread(
                        ticker,
                        future.ticker,
                        round(float(norm_delta), 2),
                        days_till_expiration,
                        round(float(norm_delta / price) * 100, 2),
                    )
                )
    ordered = sorted(result, key=lambda s: s.yld, reverse=True)
    spreads = [
        f'{s.stock_ticker} - {s.future_ticker}: {s.dividend} RUB, {s.yld}%'
        f', {s.days_till_expiration} days'
        for s in ordered
        if s.yld >= percent_threshold
    ]
    return '\n'.join(spreads)
