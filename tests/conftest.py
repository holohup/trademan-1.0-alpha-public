import pytest
# from bot.tools.classes import Figi, Spread


@pytest.fixture
def far_leg_params():
    return dict(
        figi='GZZ.1',
        ticker='GAZP',
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
def near_leg_params():
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
