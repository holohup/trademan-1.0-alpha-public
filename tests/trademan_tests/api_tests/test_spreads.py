from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

SPREAD_FIELDS = {
    'id': int,
    'sell': bool,
    'price': int,
    'amount': int,
    'ratio': int,
    'far_leg': dict,
    'near_leg': dict,
}

LEG_FIELDS = {
    'figi': str,
    'ticker': str,
    'min_price_increment': str,
    'lot': int,
    'executed': int,
    'avg_exec_price': str,
    'morning_trading': bool,
    'evening_trading': bool,
    'asset_type': str
}

LEGS = (('far_leg'), ('near_leg'))
LEG_PARAMETRIZE = pytest.mark.parametrize('leg', LEGS)


@pytest.fixture
def response(client, sample_spread):
    return client.get(reverse('spreads-list'))


@pytest.fixture
def data(response):
    return response.data[0]


@pytest.mark.django_db
def test_spreads_fields(response, data):
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == len(SPREAD_FIELDS)
    for field in SPREAD_FIELDS.keys():
        assert field in data


@pytest.mark.parametrize(
    ('field', 'kls'),
    ((name, kls) for name, kls in SPREAD_FIELDS.items()),
)
@pytest.mark.django_db
def test_spread_fields_format(data, field, kls):
    assert isinstance(data[field], kls)


@LEG_PARAMETRIZE
@pytest.mark.django_db
def test_fields_in_legs(data, leg):
    assert len(data[leg]) == len(LEG_FIELDS)
    for field in LEG_FIELDS.keys():
        assert field in data[leg]


@pytest.mark.parametrize(
    ('field', 'kls'),
    ((name, kls) for name, kls in LEG_FIELDS.items()),
)
@pytest.mark.django_db
def test_leg_field_types(data, field, kls):
    for leg in 'far_leg', 'near_leg':
        assert isinstance(data[leg][field], kls)


@pytest.mark.django_db
def test_spreads_values(data, sample_spread):
    for field in 'id', 'sell', 'price', 'amount', 'ratio':
        assert data[field] == getattr(sample_spread, field)


@LEG_PARAMETRIZE
@pytest.mark.django_db
def test_spread_legs_stats(data, sample_spread, leg):
    assert data[leg]['executed'] == getattr(
        sample_spread.stats, leg + '_executed'
    )
    assert Decimal(data[leg]['avg_exec_price']) == getattr(
        sample_spread.stats, leg + '_avg_price'
    )


@LEG_PARAMETRIZE
@pytest.mark.django_db
def test_spread_nested_values(data, sample_spread, leg):
    for field in 'figi', 'ticker', 'lot', 'morning_trading', 'evening_trading':
        assert data[leg][field] == getattr(getattr(sample_spread, leg), field)
    assert (
        Decimal(data[leg]['min_price_increment'])
        == getattr(sample_spread, leg).min_price_increment
    )
