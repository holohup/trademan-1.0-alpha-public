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
                "morning_trading": True,
                "evening_trading": True,
                "asset_type": "F",
                "executed": 10,
                "avg_exec_price": "15.0000000000",
            },
            "near_leg": {
                "figi": "BBG004730RP0",
                "ticker": "GAZP",
                "min_price_increment": "0.0100000000",
                "lot": 10,
                "morning_trading": False,
                "evening_trading": False,
                "asset_type": "S",
                "executed": 2,
                "avg_exec_price": "54.0000000000",
            },
        }
    ]


LEG_FIELDS = {
    'figi': str,
    'ticker': str,
    'min_price_increment': Decimal,
    'lot': int,
    'morning_trading': bool,
    'evening_trading': bool,
    'executed': int,
    'avg_exec_price': Decimal,
    'asset_type': str,
}

SPREAD_FIELDS = {
    'far_leg': Asset,
    'near_leg': Asset,
    'sell': bool,
    'price': int,
    'id': int,
    'ratio': int,
}

LEG_DECIMAL_FIELDS = {'min_price_increment', 'avg_exec_price'}
LEGS = ('far_leg', 'near_leg')
LEGS_PARAMETRIZE = pytest.mark.parametrize('leg', LEGS)


@pytest.fixture
def data(json_spreads_response):
    return prepare_spreads_data(json_spreads_response)


@pytest.fixture
def spread(data):
    return data[0]


@pytest.fixture
def response_data(json_spreads_response):
    return json_spreads_response[0]


def test_number_of_spreads_created(data, json_spreads_response):
    assert len(data) == len(json_spreads_response)


def test_correct_instances(data, spread):
    assert isinstance(data, list)
    assert isinstance(spread, Spread)


@pytest.mark.parametrize(
    ('attr', 'kls'),
    ((name, kls) for name, kls in SPREAD_FIELDS.items()),
)
def test_correct_field_types(spread, attr, kls):
    assert isinstance(getattr(spread, attr), kls)


@pytest.mark.parametrize(
    ('attr', 'kls'),
    ((name, kls) for name, kls in LEG_FIELDS.items()),
)
def test_correct_nested_instances(spread, attr, kls):
    assert isinstance(getattr(spread.far_leg, attr), kls)
    assert isinstance(getattr(spread.near_leg, attr), kls)


def test_correct_spread_values(spread, response_data):
    for field in SPREAD_FIELDS.keys() - set(LEGS):
        assert getattr(spread, field) == response_data[field]


@LEGS_PARAMETRIZE
def test_correct_leg_non_decimal_values(spread, response_data, leg):
    for field in LEG_FIELDS.keys() - LEG_DECIMAL_FIELDS:
        assert (
            getattr(getattr(spread, leg), field) == response_data[leg][field]
        )


@LEGS_PARAMETRIZE
def test_correct_leg_decimal_values(spread, response_data, leg):
    for decimal_field in LEG_DECIMAL_FIELDS:
        assert getattr(getattr(spread, leg), decimal_field) == Decimal(
            response_data[leg][decimal_field]
        )
