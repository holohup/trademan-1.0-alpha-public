from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_ticker_endpoint(client, sample_spread, far_leg_data):
    response = client.get(
        reverse('ticker', kwargs={'ticker': sample_spread.far_leg.ticker})
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'id', 'increment' in response.data
    assert Decimal(far_leg_data['min_price_increment']) == Decimal(
        response.data['increment']
    )
    assert len(response.data) == 12
    for field in (
        'figi',
        'ticker',
        'lot',
        'type',
        'api_trading_available',
        'short_enabled',
        'buy_enabled',
        'sell_enabled',
        'basic_asset_size',
        'name'
    ):
        assert field in response.data
        assert far_leg_data[field] == response.data[field]
