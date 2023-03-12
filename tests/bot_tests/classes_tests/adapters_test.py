from decimal import Decimal

import pytest
from tinkoff.invest import OrderDirection, OrderType
from tinkoff.invest.schemas import StopOrderDirection as SODir
from tinkoff.invest.schemas import StopOrderExpirationType as SType
from tinkoff.invest.schemas import StopOrderType as SOType
from tinkoff.invest.utils import decimal_to_quotation

from bot.tools.adapters import (OrderAdapter, SellBuyToJsonAdapter,
                                SpreadToJsonAdapter, StopOrderAdapter)
from bot.tools.classes import Asset, Spread


@pytest.mark.parametrize(
    ('asset', 'direction'),
    (
        ('sample_far_leg', OrderDirection.ORDER_DIRECTION_SELL),
        ('sample_near_leg', OrderDirection.ORDER_DIRECTION_BUY),
    ),
)
def test_limit_order_params(asset, direction, request):
    asset = request.getfixturevalue(asset)
    expected = {
        'order_type': OrderType.ORDER_TYPE_LIMIT,
        'figi': asset.figi,
        'quantity': asset.get_lots(asset.next_order_amount),
        'direction': direction,
        'price': asset.price,
    }
    adapter = OrderAdapter(asset, 'limit')
    for field in expected.keys():
        assert expected[field] == adapter.order_params[field]
    assert 'account_id' in adapter.order_params


@pytest.mark.parametrize(
    ('asset', 'direction'),
    (
        ('sample_far_leg', OrderDirection.ORDER_DIRECTION_SELL),
        ('sample_near_leg', OrderDirection.ORDER_DIRECTION_BUY),
    ),
)
def test_market_order_params(asset, direction, request):
    asset = request.getfixturevalue(asset)
    expected = {
        'order_type': OrderType.ORDER_TYPE_MARKET,
        'figi': asset.figi,
        'quantity': asset.get_lots(asset.next_order_amount),
        'direction': direction,
    }
    adapter = OrderAdapter(asset, 'market')
    for field in expected.keys():
        assert expected[field] == adapter.order_params[field]
    assert 'price' not in adapter.order_params
    assert 'account_id' in adapter.order_params


def test_long_stop_order_params(long_stop_sample):
    price = decimal_to_quotation(Decimal('105.0'))
    expected = {
        'figi': long_stop_sample.asset.figi,
        'quantity': 285,
        'direction': SODir.STOP_ORDER_DIRECTION_BUY,
        'stop_order_type': SOType.STOP_ORDER_TYPE_TAKE_PROFIT,
        'expiration_type': SType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_DATE,
    }
    adapter = StopOrderAdapter(long_stop_sample)
    assert 'account_id' in adapter.order_params
    assert 'expire_date' in adapter.order_params
    for p in 'price', 'stop_price':
        assert price.units == adapter.order_params[p].units
        assert price.nano == adapter.order_params[p].nano
    for field in expected.keys():
        assert expected[field] == adapter.order_params[field]


def test_short_stop_order_params(short_stop_sample):
    price = decimal_to_quotation(Decimal('99.99'))
    expected = {
        'figi': short_stop_sample.asset.figi,
        'quantity': 3000,
        'direction': SODir.STOP_ORDER_DIRECTION_SELL,
        'stop_order_type': SOType.STOP_ORDER_TYPE_TAKE_PROFIT,
        'expiration_type': SType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_DATE,
    }
    adapter = StopOrderAdapter(short_stop_sample)
    for p in 'price', 'stop_price':
        assert price.units == adapter.order_params[p].units
        assert price.nano == adapter.order_params[p].nano
    assert 'account_id' in adapter.order_params
    assert 'expire_date' in adapter.order_params
    for field in expected.keys():
        assert expected[field] == adapter.order_params[field]


def test_spread_to_json_adapter(sample_spread: Spread):
    dikt = SpreadToJsonAdapter(sample_spread).output
    for leg in 'far_leg', 'near_leg':
        assert getattr(sample_spread, leg).executed == dikt[leg]['executed']
        assert getattr(sample_spread, leg).avg_exec_price == Decimal(
            dikt[leg]['avg_exec_price']
        )


def test_sellbuy_to_json_adapter(sample_far_leg: Asset):
    dikt = SellBuyToJsonAdapter(sample_far_leg).output
    assert sample_far_leg.executed == dikt['executed']
    assert sample_far_leg.avg_exec_price == Decimal(dikt['avg_exec_price'])
