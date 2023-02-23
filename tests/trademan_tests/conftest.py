import pytest
from base.models import Figi, Spread


@pytest.fixture
def far_leg_data():
    return dict(
        figi='GZZ.1',
        ticker='GAZP',
        name='Gazprom',
        lot=10,
        min_price_increment=1,
        type='F',
        api_trading_available=True,
        short_enabled=True,
        buy_enabled=True,
        sell_enabled=True,
        basic_asset_size=10,
    )


@pytest.fixture
def near_leg_data():
    return dict(
        figi='GZZ.2',
        ticker='GAZP2',
        name='Gazprom',
        lot=10,
        min_price_increment=1,
        type='S',
        api_trading_available=True,
        short_enabled=True,
        buy_enabled=True,
        sell_enabled=True,
        basic_asset_size=10,
    )


@pytest.fixture
def sample_spread(near_leg_data, far_leg_data):
    far_leg_figi = Figi(**far_leg_data)
    far_leg_figi.save()
    near_leg_figi = Figi(**near_leg_data)
    near_leg_figi.save()
    return Spread.objects.create(
        asset=far_leg_figi,
        near_leg=near_leg_figi,
        exec_price=0,
        price=0,
        sell=True,
        amount=10,
    )
