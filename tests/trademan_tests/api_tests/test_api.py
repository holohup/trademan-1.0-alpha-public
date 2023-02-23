from decimal import Decimal

import pytest
from base.models import Figi, Spread
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_spreads(client, far_leg_params, near_leg_params):
    far_leg_figi = Figi(**far_leg_params)
    far_leg_figi.save()
    near_leg_figi = Figi(**near_leg_params)
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
    assert data['figi'] == far_leg_params['figi']
    assert data['ticker'] == far_leg_params['ticker']
    assert Decimal(data['increment']) == Decimal(
        far_leg_params['min_price_increment']
    )
    assert data['lot'] == far_leg_params['lot']
    assert data['near_leg_figi'] == near_leg_params['figi']
    assert data['near_leg_ticker'] == near_leg_params['ticker']
    assert Decimal(data['near_leg_increment']) == Decimal(
        near_leg_params['min_price_increment']
    )
    assert data['near_leg_lot'] == near_leg_params['lot']
    assert data['sell'] == spread.sell
    assert data['executed'] == spread.executed
    assert data['exec_price'] == spread.exec_price
    assert data['near_leg_type'] == near_leg_params['type']
    assert data['base_asset_amount'] == spread.amount
