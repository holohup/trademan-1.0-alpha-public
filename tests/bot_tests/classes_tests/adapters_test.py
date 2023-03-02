import pytest
from tinkoff.invest import OrderDirection, OrderType

from bot.tools.adapters import OrderAdapter


@pytest.mark.parametrize(
    ('asset', 'direction'),
    (
        ('sample_far_leg', OrderDirection.ORDER_DIRECTION_SELL),
        ('sample_near_leg', OrderDirection.ORDER_DIRECTION_BUY)
    )
)
def test_correct_limit_params(asset, direction, request):
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
        assert expected[field] == adapter.order_params()[field]
    assert 'account_id' in adapter.order_params()


@pytest.mark.parametrize(
    ('asset', 'direction'),
    (
        ('sample_far_leg', OrderDirection.ORDER_DIRECTION_SELL),
        ('sample_near_leg', OrderDirection.ORDER_DIRECTION_BUY)
    )
)
def test_correct_market_params(asset, direction, request):
    asset = request.getfixturevalue(asset)
    expected = {
        'order_type': OrderType.ORDER_TYPE_MARKET,
        'figi': asset.figi,
        'quantity': asset.get_lots(
            asset.next_order_amount
        ),
        'direction': direction,
    }
    adapter = OrderAdapter(asset, 'market')
    for field in expected.keys():
        assert expected[field] == adapter.order_params()[field]
    assert 'price' not in adapter.order_params()
    assert 'account_id' in adapter.order_params()
