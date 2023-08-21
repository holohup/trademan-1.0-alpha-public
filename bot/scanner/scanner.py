from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import NamedTuple, Union

from settings import (CURRENT_INTEREST_RATE, MAX_FUTURES_AHEAD,
                      PERCENT_THRESHOLD, TCS_RO_TOKEN)
from tinkoff.invest import Future, Share
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.schemas import MoneyValue, Quotation, RealExchange
from tinkoff.invest.utils import quotation_to_decimal
from tools.get_patch_prepare_data import (get_current_prices,
                                          get_current_prices_by_uid)
from tools.trading_hours import FutureTradingHours, StockTradingHours
from tools.trading_time import SimpleTradingTime


@dataclass
class LegData:
    figi: str = ''
    ticker: str = ''
    price: Decimal = Decimal('0')
    buy_margin: Decimal = Decimal('0')


@dataclass
class StockData(LegData):
    pass


@dataclass(frozen=True)
class OrderBook:
    bid: Decimal
    ask: Decimal

    @property
    def buy_price(self):
        return self.ask

    @property
    def sell_price(self):
        return self.bid


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
    can_trade: bool
    buy_price: float


class DivSpread(NamedTuple):
    sell_leg: Union[Share, Future]
    buy_leg: Future

    @property
    def _can_trade_sell_leg(self):
        return all(
            (
                self.sell_leg.api_trade_available_flag,
                self.sell_leg.sell_available_flag,
                self.sell_leg.short_enabled_flag,
            )
        )

    @property
    def _can_trade_buy_leg(self):
        return all(
            (
                self.buy_leg.api_trade_available_flag,
                self.buy_leg.buy_available_flag,
            )
        )

    @property
    def can_trade(self):
        return all((self._can_trade_sell_leg, self._can_trade_buy_leg))

    @property
    def ratio(self):
        if isinstance(self.sell_leg, Future):
            return Decimal('1')
        return quotation_to_decimal(self.buy_leg.basic_asset_size)


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


class DividendScanner:
    def __init__(self, result_limit) -> None:
        self._ir = float(CURRENT_INTEREST_RATE)
        self._result_limit = result_limit

    async def scan_spreads(self):
        await self._load_instruments()
        await self._prefilter_instruments()
        self._generate_div_spreads()
        await self._update_orderbooks()

        result = []
        for spread in self._div_spreads:
            buy_leg = spread.buy_leg
            sell_leg = spread.sell_leg
            sell_price = self._orderbooks[sell_leg.uid].sell_price
            buy_price = self._orderbooks[buy_leg.uid].buy_price
            days_till_expiration = (
                buy_leg.expiration_date - datetime.now(tz=timezone.utc)
            ).days

            time_adjusted_sell_price = (
                sell_price
                * spread.ratio
                * (
                    (1 + Decimal(self._ir / 100))
                    ** Decimal((days_till_expiration / 365))
                )
            )
            delta = buy_price - time_adjusted_sell_price
            if delta < 0:
                norm_delta = -delta / spread.ratio
                result.append(
                    DividendSpread(
                        sell_leg.ticker,
                        buy_leg.ticker,
                        round(float(norm_delta), 2),
                        days_till_expiration,
                        round(float(norm_delta / sell_price) * 100, 2),
                        can_trade=spread.can_trade,
                        buy_price=float(buy_price - sell_price * spread.ratio),
                    )
                )
        ordered = sorted(result, key=lambda s: s.yld, reverse=True)
        spreads = [
            f'{s.stock_ticker} - {s.future_ticker}: {s.dividend} RUB, {s.yld}%'
            f', {s.days_till_expiration} days, {s.can_trade},'
            f' price: {s.buy_price}'
            for s in ordered
            if s.yld >= PERCENT_THRESHOLD
        ]
        return '\n'.join(spreads[: self._result_limit])

    async def _load_instruments(self) -> None:
        shares = await get_api_response('shares')
        self._shares = shares.instruments
        futures = await get_api_response('futures')
        self._futures = futures.instruments

    def _shares_prefilter(self, share) -> bool:
        return all(
            (quotation_to_decimal(share.min_price_increment) > Decimal('0'),)
        )

    def _futures_prefilter(self, future) -> bool:
        return all(
            (
                quotation_to_decimal(future.min_price_increment)
                > Decimal('0'),
                future.basic_asset in self._filtered_shares.keys(),
                future.last_trade_date > datetime.now(tz=timezone.utc),
            )
        )

    async def _prefilter_instruments(self) -> None:
        self._filtered_shares = {
            share.ticker: share
            for share in self._shares
            if self._shares_prefilter(share) is True
        }

        self._filtered_futures = {}
        for future in self._futures:
            if not self._futures_prefilter(future):
                continue
            if future.basic_asset not in self._filtered_futures:
                self._filtered_futures[future.basic_asset] = []
            self._filtered_futures[future.basic_asset].append(future)

        for stock_ticker in self._filtered_futures:
            self._filtered_futures[stock_ticker] = sorted(
                self._filtered_futures[stock_ticker],
                key=lambda d: d.expiration_date,
            )[:MAX_FUTURES_AHEAD]
        self._filtered_shares = {
            ticker: uid
            for ticker, uid in self._filtered_shares.items()
            if ticker in self._filtered_futures.keys()
        }

    def _generate_div_spreads(self):
        self._div_spreads: list[DivSpread] = []
        self._generate_stock_future_spreads()
        self._generate_future_future_spreads()

    def _generate_future_future_spreads(self):
        for futures in self._filtered_futures.values():
            amount = len(futures)
            if amount <= 1:
                continue
            for sell_future_pos in range(amount):
                for buy_future_pos in range(sell_future_pos + 1, amount):
                    self._div_spreads.append(
                        DivSpread(
                            sell_leg=futures[sell_future_pos],
                            buy_leg=futures[buy_future_pos],
                        )
                    )

    def _generate_stock_future_spreads(self):
        for ticker, share in self._filtered_shares.items():
            for future in self._filtered_futures[ticker]:
                self._div_spreads.append(
                    DivSpread(sell_leg=share, buy_leg=future)
                )

    async def _update_orderbooks(self):
        self._orderbooks = {}
        future_prices, share_prices = {}, {}
        futures_to_update = [
            d for f in self._filtered_futures.values() for d in f
        ]
        stocks_to_update = list(self._filtered_shares.values())
        if not SimpleTradingTime(FutureTradingHours()).is_trading_now:
            future_prices = await get_current_prices_by_uid(futures_to_update)
            self._orderbooks.update(
                {
                    uid: OrderBook(bid=price, ask=price)
                    for uid, price in future_prices.items()
                }
            )
            futures_to_update = []
        if not SimpleTradingTime(StockTradingHours()).is_trading_now:
            share_prices = await get_current_prices_by_uid(stocks_to_update)
            self._orderbooks.update(
                {
                    uid: OrderBook(bid=price, ask=price)
                    for uid, price in share_prices.items()
                }
            )
            stocks_to_update = []
        uids_to_update = [
            asset.uid for asset in futures_to_update + stocks_to_update
        ]
        if uids_to_update:
            await self._update_from_orderbooks(uids_to_update)

    async def _update_from_orderbooks(self, uids_to_update):
        result = {}
        async with AsyncRetryingClient(
            TCS_RO_TOKEN, RetryClientSettings()
        ) as client:
            for uid in uids_to_update:
                if uid not in result.keys():
                    ob = await client.market_data.get_order_book(
                        instrument_id=str(uid), depth=1
                    )
                    if ob.bids:
                        bid = quotation_to_decimal(ob.bids[0].price)
                    else:
                        r = await client.market_data.get_last_prices(
                            instrument_id=[str(uid)]
                        )
                        bid = quotation_to_decimal(r.last_prices[0].price)
                    if ob.asks:
                        ask = quotation_to_decimal(ob.asks[0].price)
                    else:
                        r = await client.market_data.get_last_prices(
                            instrument_id=[str(uid)]
                        )
                        ask = quotation_to_decimal(r.last_prices[0].price)
                    result[uid] = OrderBook(
                        bid=bid,
                        ask=ask,
                    )
        self._orderbooks.update(result)


async def dividend_scan(command, args):
    if not args:
        args = '50'
    return await DividendScanner(int(args)).scan_spreads()


if __name__ == '__main__':
    import asyncio

    print(asyncio.run(dividend_scan(1, 50)))
