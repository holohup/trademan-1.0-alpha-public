from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_spreads(client, far_leg_data, near_leg_data, sample_spread):
    spread = sample_spread
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
