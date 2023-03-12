import pytest

import bot.spreads as spreads


@pytest.mark.asyncio
async def test_adjust_placed_order(sample_spread):
    sample_spread.far_leg.order_placed = False
    assert await spreads.adjust_placed_order(sample_spread) == -1
