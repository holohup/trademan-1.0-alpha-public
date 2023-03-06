from decimal import Decimal

from bot.tools.classes import Spread


def test_next_near_leg_order_amount(sample_spread: Spread):
    assert sample_spread._near_leg_next_order_amount == 470


def test_legs_cache_connected_correctly(sample_spread: Spread):
    assert sample_spread.avg_execution_price == Decimal('14')
    assert sample_spread.executed == 50


def test_cache_updates_correctly_after_new_orders(sample_spread: Spread):
    prev_avg = sample_spread.avg_execution_price
    prev_executed = sample_spread.executed
    sample_spread.far_leg.order_id = '1111'
    sample_spread.near_leg.order_id = '2222'
    sample_spread.far_leg.order_cache.update(
        sample_spread.far_leg.order_id, 10, Decimal('10')
    )
    sample_spread.near_leg.order_cache.update(
        sample_spread.near_leg.order_id, 100, Decimal('-20')
    )
    assert sample_spread.executed == 60
    assert sample_spread.avg_execution_price == Decimal(
        (prev_avg * prev_executed + Decimal(10 * 10) - Decimal(100 * (-20)))
        / sample_spread.executed
    )
