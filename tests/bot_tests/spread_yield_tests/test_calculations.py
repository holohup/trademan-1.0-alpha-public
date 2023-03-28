import datetime
from decimal import Decimal

import pytest

from bot.scanner.scanner import ProfitCounter, SpreadScanner, YieldingSpread
from bot.settings import CURRENT_INTEREST_RATE


def test_correct_init_without_arguments():
    assert SpreadScanner()._rate == Decimal(CURRENT_INTEREST_RATE)


def test_correct_init_with_argument():
    assert SpreadScanner('8')._rate == Decimal('8')


def test_correct_error_when_argument_is_not_numeric():
    with pytest.raises(ValueError):
        SpreadScanner('lalala')


def test_correct_days_till_profit_count(
    sample_f_f_yielding_spread: YieldingSpread,
):
    counter = ProfitCounter(sample_f_f_yielding_spread)
    assert (
        counter._days_till_profit
        == (
            sample_f_f_yielding_spread.far_leg.expiration_date
            - datetime.datetime.now(tz=datetime.timezone.utc)
        ).days
    )


def test_correct_total_margin(sample_s_f_yielding_spread):
    counter = ProfitCounter(sample_s_f_yielding_spread)
    assert (
        counter._total_margin
        == sample_s_f_yielding_spread.far_leg.sell_margin
        + sample_s_f_yielding_spread.near_leg.buy_margin
        * sample_s_f_yielding_spread.far_to_near_ratio
    )


def test_total_profit(sample_f_f_yielding_spread, sample_s_f_yielding_spread):
    counter = ProfitCounter(sample_f_f_yielding_spread)
    assert counter._total_profit == Decimal('13')
    counter = ProfitCounter(sample_s_f_yielding_spread)
    assert counter._total_profit == Decimal('13')


def test_correct_count_profit(sample_yielding_spread):
    counter = ProfitCounter(sample_yielding_spread)
    margin, profit = counter.calculate_profit()
    assert margin == Decimal('70000')
    assert int(profit) == 100
