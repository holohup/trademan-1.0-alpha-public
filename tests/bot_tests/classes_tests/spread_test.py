from decimal import Decimal

from bot.tools.classes import Spread


def test_next_near_leg_order_amount(sample_spread: Spread):
    assert sample_spread._near_leg_next_order_amount == 400


def test_cache_connected_correctly(sample_spread: Spread):
    assert sample_spread.avg_execution_price == Decimal('150')
    assert sample_spread.executed == 15


def test_cache_updates_correctly_after_new_orders(sample_spread: Spread):
    sample_spread.far_leg.order_id = '1111'
    sample_spread.near_leg.order_id = '2222'
    sample_spread.far_leg.order_cache.update(
        sample_spread.far_leg.order_id, 10, Decimal('10')
    )
    sample_spread.near_leg.order_cache.update(
        sample_spread.near_leg.order_id, 100, Decimal('-20')
    )
    sample_spread._update_cache()
    assert sample_spread.executed == 25
    assert sample_spread.avg_execution_price == Decimal(
        (
            sample_spread.cache.executed_by_id('initial')
            * sample_spread.cache.price_by_id('initial')
            + 10 * Decimal('10') - 100 * Decimal('-20')
        )
        / sample_spread.executed
    )
