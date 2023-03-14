import pytest

from tests.bot_tests.classes_tests.factories import SpreadFactory
from tests.bot_tests.classes_tests.trading_time_test import OFFSET


@pytest.mark.parametrize('hour', (((10, 5), (12, 00), (15, 00))))
def test_is_trading_now_when_all_legs_are_trading(hour, patch_tradingtime):
    spread = SpreadFactory.build()
    patch_tradingtime(6, hour)
    assert spread.is_trading_now is True


@pytest.mark.parametrize(
    'hour', (((14, 3), (18, 50), (10, 00), (0, 0), (23, 50)))
)
def test_is_trading_now_when_one_or_both_the_legs_not_trading(
    hour, patch_tradingtime
):
    spread = SpreadFactory.build()
    patch_tradingtime(6, hour)
    assert spread.is_trading_now is False


@pytest.mark.parametrize('hour', ((12, 00), (15, 00), (10, 5)))
def test_seconds_till_trading_starts_when_both_legs_trade(
    hour, patch_tradingtime
):
    spread = SpreadFactory.build()
    patch_tradingtime(6, hour)
    assert spread.seconds_till_trading_starts == 0


@pytest.mark.parametrize(
    ('hour', 'result'),
    (
        ((10, 0), OFFSET),
        ((14, 0), 5 * 60 + OFFSET),
        ((20, 50), OFFSET + 10 * 60 + 13 * 60 * 60),
    ),
)
def test_seconds_till_trading_starts_when_one_leg_doesnt_trade(
    hour, result, patch_tradingtime
):
    spread = SpreadFactory.build()
    patch_tradingtime(6, hour)
    assert spread.seconds_till_trading_starts == result


@pytest.mark.parametrize(
    ('day', 'hour', 'result'),
    (
        (6, (9, 30), OFFSET + 30 * 60),
        (5, (14, 0), OFFSET + 20 * 60 * 60),
        (6, (23, 50), OFFSET + 10 * 60 + 10 * 60 * 60),
    ),
)
def test_seconds_till_trading_starts_when_both_legs_dont_trade(
    day, hour, result, patch_tradingtime
):
    spread = SpreadFactory.build()
    patch_tradingtime(day, hour)
    assert spread.seconds_till_trading_starts == result
