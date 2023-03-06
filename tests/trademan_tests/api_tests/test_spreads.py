from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.fixture
def response(client, sample_spread):
    return client.get(reverse('spreads-list'))


@pytest.fixture
def data(response):
    return response.data[0]


@pytest.mark.django_db
def test_spreads_fields(response, data):
    assert response.status_code == status.HTTP_200_OK
    assert len(data) == 7
    for field in (
        'id',
        'sell',
        'price',
        'amount',
        'ratio',
        'far_leg',
        'near_leg',
    ):
        assert field in data


@pytest.mark.parametrize(
    ('field', 'kls'),
    (
        ('id', int),
        ('sell', bool),
        ('price', int),
        ('amount', int),
        ('ratio', int),
        ('far_leg', dict),
        ('near_leg', dict),
    ),
)
@pytest.mark.django_db
def test_spread_fields_format(data, field, kls):
    assert isinstance(data[field], kls)


@pytest.mark.parametrize('leg', (('far_leg'), ('near_leg')))
@pytest.mark.django_db
def test_fields_in_legs(data, leg):
    assert len(data[leg]) == 6
    for field in (
        'figi',
        'ticker',
        'min_price_increment',
        'lot',
        'executed',
        'avg_exec_price',
    ):
        assert field in data[leg]


@pytest.mark.parametrize(
    ('field', 'kls'),
    (
        ('figi', str),
        ('ticker', str),
        ('min_price_increment', str),
        ('lot', int),
        ('executed', int),
        ('avg_exec_price', str),
    ),
)
@pytest.mark.django_db
def test_leg_field_types(data, field, kls):
    assert isinstance(data['far_leg'], dict)
    assert isinstance(data['near_leg'], dict)
    for leg in 'far_leg', 'near_leg':
        assert isinstance(data[leg][field], kls)


@pytest.mark.django_db
def test_spreads_values(data, sample_spread):
    for field in 'id', 'sell', 'price', 'amount', 'ratio':
        assert data[field] == getattr(sample_spread, field)


@pytest.mark.django_db
def test_spread_stats(data, sample_spread):
    assert data['far_leg']['executed'] == sample_spread.stats.far_leg_executed
    assert (
        data['near_leg']['executed'] == sample_spread.stats.near_leg_executed
    )
    assert (
        Decimal(data['far_leg']['avg_exec_price'])
        == sample_spread.stats.far_leg_avg_price
    )

    assert (
        Decimal(data['near_leg']['avg_exec_price'])
        == sample_spread.stats.near_leg_avg_price
    )


@pytest.mark.parametrize('leg', (('far_leg'), ('near_leg')))
@pytest.mark.django_db
def test_spread_nested_values(data, sample_spread, leg):
    for field in 'figi', 'ticker', 'lot':
        assert data[leg][field] == getattr(getattr(sample_spread, leg), field)
    assert (
        Decimal(data[leg]['min_price_increment'])
        == getattr(sample_spread, leg).min_price_increment
    )
