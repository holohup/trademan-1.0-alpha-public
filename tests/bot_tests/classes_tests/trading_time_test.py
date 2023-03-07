from datetime import datetime

import pytest

from bot.tools.trading_time import ZONE, TradingTime
from tests.bot_tests.classes_tests.factories import AssetFactory

NOON_HOUR = 12
MIDNIGHT_HOUR = 0
MORNING_HOUR = 9
EVENING_HOUR = 21


def generic_trading_time_test(day_of_month, hours_time, asset_params=None):
    if not asset_params:
        asset_params = {}
    asset = AssetFactory(**asset_params)
    pytest.MonkeyPatch().setattr(
        TradingTime,
        '_current_time',
        datetime(2023, 3, day_of_month, hours_time, 0, 0, tzinfo=ZONE),
    )
    tt = TradingTime(asset)
    return tt.is_trading_now


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
