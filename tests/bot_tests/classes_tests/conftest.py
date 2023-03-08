from decimal import Decimal
from typing import NamedTuple

import pytest


class AssetPreset(NamedTuple):
    field: str
    expected_type: type
    value: any


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
