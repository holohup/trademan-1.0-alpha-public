from datetime import datetime

import pytest

from bot.tools.trading_time import MOSCOW_ZONE, TIME_OFFSET, TradingTime
from tests.bot_tests.classes_tests.factories import AssetFactory

NOON = (12, 0, 0)
MIDNIGHT = (0, 0, 0)
MORNING = (9, 5, 0)
EVENING = (21, 0, 0)
AFTER_CLOSE = (23, 55, 0)
OFFSET = TIME_OFFSET.seconds
EXTRA_HOURS = pytest.mark.parametrize('hour', ((MORNING), (EVENING)))
FUTURES_CLEARING_TIMES = ((14, 1, 0), (18, 55, 0), (19, 4, 0))
STOCKS_CLEARING_TIMES = ((18, 45, 0), (18, 55, 0), (19, 2, 0))

FUTURE_PARAMS = dict(
    morning_trading=True, evening_trading=True, asset_type='F'
)
STOCK_PARAMS = dict(
    morning_trading=False, evening_trading=False, asset_type='S'
)


class GenericTradingTimeTester:
    def __init__(self, day, tyme, asset_params={}) -> None:
        self._day = day
        self._time = tyme
        self._params = asset_params

    @property
    def create_tradingtime_object(self) -> TradingTime:
        dt = datetime(2023, 3, self._day, *self._time, tzinfo=MOSCOW_ZONE)
        asset = AssetFactory.build(**self._params)
        pytest.MonkeyPatch().setattr(TradingTime, '_current_datetime', dt)
        return TradingTime(asset)

    @property
    def is_trading_now(self) -> bool:
        return self.create_tradingtime_object.is_trading_now

    @property
    def midnights_count_till_trading_starts(self) -> int:
        return (
            self.create_tradingtime_object._midnights_count_till_trading_day
        )

    @property
    def seconds_till_trading_starts(self) -> int:
        return self.create_tradingtime_object.seconds_till_trading_starts


@pytest.mark.parametrize('workday_of_month', ((1), (2), (3), (6), (7)))
def test_noon_is_trading_time_on_workdays(workday_of_month):
    assert (
        GenericTradingTimeTester(workday_of_month, NOON).is_trading_now is True
    )


@pytest.mark.parametrize('day_of_month', ((1), (2), (3), (4), (5), (6), (7)))
def test_midnight_is_not_trading_time(day_of_month):
    assert (
        GenericTradingTimeTester(day_of_month, MIDNIGHT).is_trading_now
        is False
    )


@pytest.mark.parametrize('weekend_day_of_month', ((4), (5)))
def test_weekends_are_not_trading(weekend_day_of_month):
    assert (
        GenericTradingTimeTester(weekend_day_of_month, NOON).is_trading_now
        is False
    )


@pytest.mark.parametrize(
    ('hour', 'm_trading', 'e_trading', 'result'),
    (
        (MORNING, True, False, True),
        (MORNING, False, True, False),
        (EVENING, True, False, False),
        (EVENING, True, True, True),
    ),
)
def test_stock_trading_time_on_morn_and_evn(
    hour, m_trading, e_trading, result
):
    params = dict(
        morning_trading=m_trading, evening_trading=e_trading, asset_type='S'
    )
    assert GenericTradingTimeTester(1, hour, params).is_trading_now is result


@EXTRA_HOURS
def test_generic_stock_not_trading_extra_hours(hour):
    assert (
        GenericTradingTimeTester(1, hour, STOCK_PARAMS).is_trading_now is False
    )


@EXTRA_HOURS
def test_generic_future_trading_extra_hours(hour):
    assert (
        GenericTradingTimeTester(1, hour, FUTURE_PARAMS).is_trading_now is True
    )


@pytest.mark.parametrize('clearing_hour', FUTURES_CLEARING_TIMES)
def test_future_not_trading_on_clearing(clearing_hour):
    assert (
        GenericTradingTimeTester(
            1, clearing_hour, FUTURE_PARAMS
        ).is_trading_now
        is False
    )


@pytest.mark.parametrize('clearing_hour', STOCKS_CLEARING_TIMES)
def test_stock_not_trading_on_clearing(clearing_hour):
    assert (
        GenericTradingTimeTester(1, clearing_hour, STOCK_PARAMS).is_trading_now
        is False
    )


def test_midnights_till_trading_starts_on_tradingtime():
    assert (
        GenericTradingTimeTester(
            6, NOON, STOCK_PARAMS
        ).midnights_count_till_trading_starts
        == 0
    )


@pytest.mark.parametrize('time', (MIDNIGHT, MORNING, NOON, EVENING))
def test_midnights_till_trading_starts_before_close(time):
    assert (
        GenericTradingTimeTester(
            6, time, FUTURE_PARAMS
        ).midnights_count_till_trading_starts
        == 0
    )


@pytest.mark.parametrize(
    ('day', 'result'), ((1, 0), (2, 0), (3, 0), (4, 2), (5, 1), (6, 0), (7, 0))
)
def test_midnights_till_trading_starts_noon(day, result):
    assert (
        GenericTradingTimeTester(
            day, NOON, FUTURE_PARAMS
        ).midnights_count_till_trading_starts
        == result
    )


@pytest.mark.parametrize(
    ('day', 'result'), ((1, 1), (2, 1), (3, 3), (4, 2), (5, 1), (6, 1), (7, 1))
)
def test_midnights_till_trading_starts_after_close(day, result):
    assert (
        GenericTradingTimeTester(
            day, AFTER_CLOSE, FUTURE_PARAMS
        ).midnights_count_till_trading_starts
        == result
    )


@pytest.mark.parametrize(
    ('day', 'result'), ((1, 1), (2, 5), (3, 4), (4, 3), (5, 2), (6, 1), (7, 1))
)
def test_midnights_till_trading_with_other_tradedays(day, result, monkeypatch):
    monkeypatch.setattr('bot.tools.trading_time.TRADE_DAYS', (1, 3))
    assert (
        GenericTradingTimeTester(
            day, AFTER_CLOSE, FUTURE_PARAMS
        ).midnights_count_till_trading_starts
        == result
    )


def test_stocks_seconds_till_open_is_zero_on_trading_time():
    assert (
        GenericTradingTimeTester(
            6, NOON, STOCK_PARAMS
        ).seconds_till_trading_starts
        == 0
    )


def test_future_seconds_till_trading_is_open_from_monday_midnight():
    assert (
        GenericTradingTimeTester(
            6, MIDNIGHT, FUTURE_PARAMS
        ).seconds_till_trading_starts
        == 9 * 60 * 60 + OFFSET
    )


@pytest.mark.parametrize(
    ('pause_time', 'asset_type', 'result'),
    (
        ((19, 0, 0), FUTURE_PARAMS, 15 * 60 + OFFSET),
        ((9, 00), STOCK_PARAMS, 60 * 60 + OFFSET),
        ((8, 00), FUTURE_PARAMS, 60 * 60 + OFFSET),
        (MIDNIGHT, STOCK_PARAMS, 10 * 60 * 60 + OFFSET),
        ((14, 3, 30), FUTURE_PARAMS, 390 + OFFSET),
        ((14, 3, 30), STOCK_PARAMS, 0),
        ((10, 00), STOCK_PARAMS, OFFSET),
        ((10, 00), FUTURE_PARAMS, 0),
    ),
)
def test_assets_seconds_till_trading_between_sessions(
    pause_time, asset_type, result
):
    assert (
        GenericTradingTimeTester(
            6, pause_time, asset_type
        ).seconds_till_trading_starts
        == result
    )


@pytest.mark.parametrize(
    ('day', 'tyme', 'result'),
    (
        (3, (23, 51), 2 * 24 * 60 * 60 + 9 * 60 + 10 * 60 * 60),
        (4, (12, 00), 2 * 24 * 60 * 60 - 2 * 60 * 60),
        (5, (15, 00), 19 * 60 * 60),
        (6, (23, 50), 10 * 60 + 10 * 60 * 60),
        (4, (0, 0), 2 * 24 * 60 * 60 + 10 * 60 * 60),
        (5, (0, 0), 34 * 60 * 60),
        (6, (0, 0), 10 * 60 * 60),
    ),
)
def test_stock_seconds_before_open_through_weekends(day, tyme, result):
    assert (
        GenericTradingTimeTester(
            day, tyme, STOCK_PARAMS
        ).seconds_till_trading_starts
        == result + OFFSET
    )
