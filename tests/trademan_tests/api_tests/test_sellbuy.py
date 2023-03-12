from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

SELLBUY_FIELDS = {
    'id': int,
    'figi': str,
    'ticker': str,
    'min_price_increment': str,
    'lot': int,
    'sell': bool,
    'amount': int,
    'executed': int,
    'avg_exec_price': str,
    'asset_type': str,
    'morning_trading': bool,
    'evening_trading': bool,
}


@pytest.fixture
def response(client, sellbuy_sample):
    return client.get(reverse('sellbuy-list'))


@pytest.fixture
def data(response, sellbuy_sample):
    return response.data[0]


@pytest.mark.django_db
def test_spreads_fields(response, data):
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(SELLBUY_FIELDS)
    for field in SELLBUY_FIELDS.keys():
        assert field in data


@pytest.mark.parametrize(
    ('field', 'kls'),
    ((name, kls) for name, kls in SELLBUY_FIELDS.items()),
)
@pytest.mark.django_db
def test_sellbuy_fields_format(data, field, kls):
    assert isinstance(data[field], kls)


@pytest.mark.django_db
def test_non_decimal_field_values(data, sellbuy_sample):
    assert data['id'] == sellbuy_sample.id
    assert sellbuy_sample.active is True
    for field in 'sell', 'amount', 'executed':
        assert data[field] == getattr(sellbuy_sample, field)
    for field in 'executed', 'avg_exec_price':
        assert Decimal(data[field]) == getattr(sellbuy_sample, field)
    for field in (
        'figi',
        'ticker',
        'lot',
        'asset_type',
        'morning_trading',
        'evening_trading',
    ):
        assert data[field] == getattr(sellbuy_sample.asset, field)


@pytest.mark.parametrize(
    ('executed', 'price', 'active'),
    (
        (600, Decimal('170'), True),
        (1000, Decimal('180'), False),
        (1500, Decimal('190'), False),
    ),
)
@pytest.mark.django_db
def test_sellbuy_active_and_price_upon_execution(
    sellbuy_sample, client, executed, price, active
):
    payload = {'executed': executed, 'avg_exec_price': price}
    response = client.patch(
        reverse('sellbuy-detail', kwargs={'pk': sellbuy_sample.id}),
        payload,
        content_type='application/json',
    )
    sellbuy_sample.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert sellbuy_sample.active == active
    assert sellbuy_sample.avg_exec_price == price
    assert sellbuy_sample.executed == executed
