from datetime import datetime
from decimal import Decimal
from typing import Any, NamedTuple

import pytest

from bot.tools.trading_time import MOSCOW_ZONE, TradingTime


class AssetPreset(NamedTuple):
    field: str
    expected_type: type
    value: Any


@pytest.fixture
def asset_sample1():
    return {
        'figi': AssetPreset('figi', str, 's1'),
        'min_price_increment': AssetPreset(
            'min_price_increment', Decimal, Decimal('1')
        ),
        'ticker': AssetPreset('ticker', str, 'SONE'),
        'lot': AssetPreset('lot', int, 10),
        'id': AssetPreset('id', int, 1),
        'price': AssetPreset('price', Decimal, Decimal(100)),
        'sell': AssetPreset('sell', bool, False),
        'amount': AssetPreset('amount', int, 100),
        'executed': AssetPreset('executed', int, 10),
    }


def patch_tradingtime_currenttime_for_march_2003_day_and_time(day, hour):
    dt = datetime(2023, 3, day, *hour, tzinfo=MOSCOW_ZONE)
    pytest.MonkeyPatch().setattr(TradingTime, '_current_datetime', dt)


@pytest.fixture()
def patch_tradingtime():
    return patch_tradingtime_currenttime_for_march_2003_day_and_time
