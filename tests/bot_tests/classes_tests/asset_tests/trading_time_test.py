import pytest

from tests.bot_tests.classes_tests.factories import AssetFactory
from tests.bot_tests.classes_tests.trading_time_test import (
    AFTER_CLOSE, EVENING, FUTURE_PARAMS, FUTURES_CLEARING_TIMES, MORNING, NOON,
    OFFSET, STOCK_PARAMS, STOCKS_CLEARING_TIMES)


@pytest.mark.parametrize(
    ('preset', 'hour', 'result'),
    (
        (STOCK_PARAMS, NOON, True),
        (STOCK_PARAMS, EVENING, False),
        (STOCK_PARAMS, AFTER_CLOSE, False),
        (FUTURE_PARAMS, NOON, True),
        (FUTURE_PARAMS, EVENING, True),
        (FUTURE_PARAMS, AFTER_CLOSE, False),
    ),
)
def test_asset_is_trading_now(preset, hour, result, patch_tradingtime):
    asset = AssetFactory.build(**preset)
    patch_tradingtime(6, hour)
    assert asset.is_trading_now is result


@pytest.mark.parametrize(
    ('preset', 'clearing_hours'),
    (
        (STOCK_PARAMS, STOCKS_CLEARING_TIMES),
        (FUTURE_PARAMS, FUTURES_CLEARING_TIMES),
    ),
)
def test_asset_is_trading_now_on_clearing_times(
    preset, clearing_hours, patch_tradingtime
):
    for hour in clearing_hours:
        asset = AssetFactory.build(**preset)
        patch_tradingtime(6, hour)
        assert asset.is_trading_now is False


@pytest.mark.parametrize(
    ('preset', 'hour', 'result'),
    (
        (STOCK_PARAMS, NOON, 0),
        (STOCK_PARAMS, MORNING, 55 * 60 + OFFSET),
        (FUTURE_PARAMS, MORNING, 0),
        (FUTURE_PARAMS, (14, 0, 0), 10 * 60 + OFFSET),
    ),
)
def test_seconds_till_trading_starts(preset, hour, result, patch_tradingtime):
    asset = AssetFactory.build(**preset)
    patch_tradingtime(6, hour)
    assert asset.seconds_till_trading_starts == result
