from decimal import Decimal

import aiohttp
import pytest

from bot.place_stops import LONG_STOP_PARAMS, SHORT_STOP_PARAMS
from bot.tools.classes import Asset, Spread, StopOrder


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
        min_price_increment=Decimal('0.01'),
        lot=10,
        price=Decimal('200'),
        id=1,
        sell=True,
        amount=100,
        executed=50,
        avg_exec_price=Decimal('20'),
        order_placed=False,
        order_id=None,
        asset_type='F'
    )


@pytest.fixture
def sample_near_leg():
    return Asset(
        ticker='GZZ4',
        figi='GZZGIGNGR54',
        min_price_increment=Decimal('0.01'),
        lot=1,
        price=Decimal('200'),
        id=2,
        sell=False,
        amount=100,
        executed=30,
        avg_exec_price=Decimal('10'),
        order_placed=False,
        order_id=None,
        asset_type='S'
    )


@pytest.fixture
def sample_spread(sample_far_leg, sample_near_leg):
    return Spread(
        far_leg=sample_far_leg,
        near_leg=sample_near_leg,
        sell=sample_far_leg.sell,
        price=100,
        id=3,
        ratio=10,
        amount=100
    )


@pytest.fixture
def long_stop_sample(sample_far_leg):
    return StopOrder(
        asset=sample_far_leg,
        price=Decimal('105.001'),
        sum=300000,
        params=LONG_STOP_PARAMS
    )


@pytest.fixture
def short_stop_sample(sample_near_leg):
    return StopOrder(
        asset=sample_near_leg,
        price=Decimal('99.999'),
        sum=300000,
        params=SHORT_STOP_PARAMS
    )
