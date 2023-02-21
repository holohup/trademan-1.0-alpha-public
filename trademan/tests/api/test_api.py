from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from base.models import Figi, Spread


@pytest.mark.django_db
def test_spreads(client):
    far_leg_data = dict(
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
    near_leg_data = dict(
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
    far_leg_figi = Figi(**far_leg_data)
    far_leg_figi.save()
    near_leg_figi = Figi(**near_leg_data)
    near_leg_figi.save()
    spread = Spread.objects.create(
        asset=far_leg_figi,
        near_leg=near_leg_figi,
        exec_price=0,
        price=0,
        sell=True,
        amount=10,
    )
    response = client.get(reverse('spreads-list'))
    assert response.status_code == status.HTTP_200_OK
    data = response.data[0]
    assert data['id'] == spread.id
    assert data['figi'] == far_leg_data['figi']
    assert data['ticker'] == far_leg_data['ticker']
    assert Decimal(data['increment']) == Decimal(
        far_leg_data['min_price_increment']
    )
    assert data['lot'] == far_leg_data['lot']
    assert data['near_leg_figi'] == near_leg_data['figi']
    assert data['near_leg_ticker'] == near_leg_data['ticker']
    assert Decimal(data['near_leg_increment']) == Decimal(
        near_leg_data['min_price_increment']
    )
    assert data['near_leg_lot'] == near_leg_data['lot']
    assert data['sell'] == spread.sell
    assert data['executed'] == spread.executed
    assert data['exec_price'] == spread.exec_price
    assert data['near_leg_type'] == near_leg_data['type']
    assert data['base_asset_amount'] == spread.amount
