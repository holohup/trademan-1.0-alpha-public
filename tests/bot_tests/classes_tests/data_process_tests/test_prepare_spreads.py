from decimal import Decimal

import pytest
from tools.classes import Asset, Spread
from tools.get_patch_prepare_data import prepare_spreads_data


@pytest.fixture
def json_spreads_response():
    return [
        {
            "id": 10,
            "sell": False,
            "price": 55,
            "amount": 20,
            "ratio": 100,
            "far_leg": {
                "figi": "FUTGAZR03230",
                "ticker": "GZH3",
                "min_price_increment": "1.0000000000",
                "lot": 1,
                "executed": 10,
                "avg_exec_price": "15.0000000000",
            },
            "near_leg": {
                "figi": "BBG004730RP0",
                "ticker": "GAZP",
                "min_price_increment": "0.0100000000",
                "lot": 10,
                "executed": 2,
                "avg_exec_price": "54.0000000000",
            },
        }
    ]


@pytest.fixture
def data(json_spreads_response):
    return prepare_spreads_data(json_spreads_response)


@pytest.mark.parametrize(
    ('attr', 'kls'),
    (
        ('far_leg', Asset),
        ('near_leg', Asset),
        ('sell', bool),
        ('price', int),
        ('id', int),
        ('ratio', int),
    ),
)
def test_correct_instances(data, attr, kls):
    for spread in data:
        assert isinstance(spread, Spread)
        assert isinstance(getattr(spread, attr), kls)


@pytest.mark.parametrize(
    ('attr', 'kls'),
    (
        ('figi', str),
        ('ticker', str),
        ('increment', Decimal),
        ('lot', int),
        ('executed', int),
        ('avg_exec_price', Decimal),
    ),
)
def test_correct_nested_instances(data, attr, kls):
    for spread in data:
        assert isinstance(getattr(spread.far_leg, attr), kls)
        assert isinstance(getattr(spread.near_leg, attr), kls)


def test_correct_class_variables_init(data, json_spreads_response):
    response_data = json_spreads_response[0]
    spread = data[0]
    for field in 'id', 'amount', 'price', 'ratio', 'sell':
        assert getattr(spread, field) == response_data[field]
    for field in 'figi', 'ticker', 'lot', 'executed':
        assert (
            getattr(spread.far_leg, field) == response_data['far_leg'][field]
        )
        assert (
            getattr(spread.near_leg, field) == response_data['near_leg'][field]
        )
    for leg in 'far_leg', 'near_leg':
        assert getattr(spread, leg).increment == Decimal(
            response_data[leg]['min_price_increment']
        )
        assert getattr(spread, leg).avg_exec_price == Decimal(
            response_data[leg]['avg_exec_price']
        )
