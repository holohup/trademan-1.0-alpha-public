from decimal import Decimal

import pytest
from tools.classes import Asset
from tools.get_patch_prepare_data import prepare_assets_data


@pytest.fixture
def json_sellbuy_response():
    return [
        {
            'id': 11,
            'figi': 'TESTGAZP',
            'ticker': 'GUZP',
            'min_price_increment': '0.05',
            'lot': 10,
            'sell': True,
            'amount': 1000,
            'executed': 100,
            'avg_exec_price': '159.99',
            'asset_type': 'S',
            'morning_trading': False,
            'evening_trading': True,
        }
    ]


SELLBUY_FIELDS = {
    'id': int,
    'figi': str,
    'ticker': str,
    'min_price_increment': Decimal,
    'lot': int,
    'sell': bool,
    'amount': int,
    'executed': int,
    'avg_exec_price': Decimal,
    'asset_type': str,
    'morning_trading': bool,
    'evening_trading': bool,
}

DECIMAL_FIELDS = {'min_price_increment', 'avg_exec_price'}


@pytest.fixture
def data(json_sellbuy_response):
    return prepare_assets_data(json_sellbuy_response)


@pytest.fixture
def sellbuy(data):
    return data[0]


@pytest.fixture
def response_data(json_sellbuy_response):
    return json_sellbuy_response[0]


def test_number_of_sellbuy_created(data, json_sellbuy_response):
    assert len(data) == len(json_sellbuy_response)


def test_correct_instances(data, sellbuy):
    assert isinstance(data, list)
    assert isinstance(sellbuy, Asset)


@pytest.mark.parametrize(
    ('attr', 'kls'),
    ((name, kls) for name, kls in SELLBUY_FIELDS.items()),
)
def test_correct_field_types(sellbuy, attr, kls):
    assert isinstance(getattr(sellbuy, attr), kls)


def test_correct_sellbuy_values(sellbuy, response_data):
    for field in SELLBUY_FIELDS.keys() - DECIMAL_FIELDS:
        assert getattr(sellbuy, field) == response_data[field]
    for field in DECIMAL_FIELDS:
        assert getattr(sellbuy, field) == Decimal(response_data[field])
