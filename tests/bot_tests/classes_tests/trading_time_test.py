from datetime import datetime

import pytest

from bot.tools.trading_time import ZONE, TradingTime
from tests.bot_tests.classes_tests.factories import AssetFactory

NOON_HOUR = (12, 0, 0)
MIDNIGHT_HOUR = (0, 0, 0)
MORNING_HOUR = (9, 0, 0)
EVENING_HOUR = (21, 0, 0)

EXTRA_HOURS = pytest.mark.parametrize('hour', ((MORNING_HOUR), (EVENING_HOUR)))
FUTURES_CLEARING_TIMES = ((14, 1, 0), (18, 55, 0), (19, 4, 0))
STOCKS_CLEARING_TIMES = ((18, 45, 0), (18, 55, 0), (19, 2, 0))

FUTURE_PARAMS = dict(
    morning_trading=True, evening_trading=True, asset_type='F'
)
STOCK_PARAMS = dict(
    morning_trading=False, evening_trading=False, asset_type='S'
)


def generic_trading_time_test(day_of_month, time, asset_params={}):
    dt = datetime(2023, 3, day_of_month, *time, tzinfo=ZONE)
    asset = AssetFactory.build(**asset_params)
    pytest.MonkeyPatch().setattr(TradingTime, '_current_time', dt)
    return TradingTime(asset).is_trading_now


@pytest.mark.parametrize('workday_of_month', ((1), (2), (3), (6), (7)))
def test_noon_is_trading_time_on_workdays(workday_of_month):
    assert generic_trading_time_test(workday_of_month, NOON_HOUR) is True


@pytest.mark.parametrize('day_of_month', ((1), (2), (3), (4), (5), (6), (7)))
def test_midnight_is_not_trading_time(day_of_month):
    assert generic_trading_time_test(day_of_month, MIDNIGHT_HOUR) is False


@pytest.mark.parametrize('weekend_day_of_month', ((4), (5)))
def test_weekends_are_not_trading(weekend_day_of_month):
    assert generic_trading_time_test(weekend_day_of_month, NOON_HOUR) is False


@pytest.mark.parametrize(
    ('hour', 'm_trading', 'e_trading', 'result'),
    (
        (MORNING_HOUR, True, False, True),
        (MORNING_HOUR, False, True, False),
        (EVENING_HOUR, True, False, False),
        (EVENING_HOUR, True, True, True),
    ),
)
def test_trading_time_on_morn_and_evn_sess(hour, m_trading, e_trading, result):
    params = dict(morning_trading=m_trading, evening_trading=e_trading)
    assert generic_trading_time_test(1, hour, params) == result


@EXTRA_HOURS
def test_generic_stock_not_trading_extra_hours(hour):
    assert generic_trading_time_test(1, hour, STOCK_PARAMS) is False


@EXTRA_HOURS
def test_generic_future_trading_extra_hours(hour):
    assert generic_trading_time_test(1, hour, FUTURE_PARAMS) is True


@pytest.mark.parametrize('clearing_hour', FUTURES_CLEARING_TIMES)
def test_future_not_trading_on_clearing(clearing_hour):
    assert generic_trading_time_test(1, clearing_hour, FUTURE_PARAMS) is False


@pytest.mark.parametrize('clearing_hour', STOCKS_CLEARING_TIMES)
def test_stock_not_trading_on_clearing(clearing_hour):
    assert generic_trading_time_test(1, clearing_hour, STOCK_PARAMS) is False
