from decimal import Decimal

import aiohttp
import pytest

from bot.tools.classes import Asset, Spread


@pytest.fixture
async def mock_client_session(mocker):
    mock_response = mocker.MagicMock()
    mock_response.__aenter__.return_value.status = 200
    mocker.patch('aiohttp.ClientSession.get', return_value=mock_response)
    return aiohttp.ClientSession()


@pytest.fixture
def sample_far_leg():
    return Asset(
        ticker='GAZP',
        figi='GZZGIGNGR53',
        increment=Decimal('0.01'),
        lot=10,
        price=Decimal('200'),
        id=1,
        sell=True,
        amount=100,
        executed=10,
        order_placed=False,
        order_id=None,
    )


@pytest.fixture
def sample_near_leg():
    return Asset(
        ticker='GZZ4',
        figi='GZZGIGNGR54',
        increment=Decimal('0.01'),
        lot=1,
        price=Decimal('200'),
        id=2,
        sell=False,
        amount=100,
        executed=10,
        order_placed=False,
        order_id=None,
    )


@pytest.fixture
def sample_spread(sample_far_leg, sample_near_leg):
    return Spread(
        far_leg=sample_far_leg,
        near_leg=sample_near_leg,
        sell=sample_far_leg.sell,
        price=100,
        id=3,
        amount=10,
        executed=15,
        near_leg_type='S',
        base_asset_amount=10,
        exec_price=150,
    )
