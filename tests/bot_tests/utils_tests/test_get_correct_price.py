from decimal import Decimal

import pytest
from tinkoff.invest.schemas import Quotation

from bot.tools.utils import get_correct_price


@pytest.mark.parametrize(
    'incorrect_values',
    (
        (-100, 10),
        (Decimal(-100), Decimal(10)),
        (Decimal(100), Decimal(-10)),
        (Decimal(-100), Decimal(-10)),
        (100, 10),
        (100.1, 0.1),
        (100, 10.0),
        (100.0, 10),
    )
)
def test_incorrect_price_and_increment_values(incorrect_values):
    with pytest.raises(ValueError):
        get_correct_price(*incorrect_values)


def test_zero_increment():
    with pytest.raises(ValueError):
        get_correct_price(Decimal('100'), Decimal('0'))


def test_returns_quotation():
    assert isinstance(
        get_correct_price(Decimal('100'), Decimal('10')), Quotation
    )


def test_correct_result():
    result = get_correct_price(Decimal('100'), Decimal('10'))
    assert result.units == 100
    assert result.nano == 0
    result = get_correct_price(Decimal('99'), Decimal('10'))
    assert result.units == 90
    assert result.nano == 0
    result = get_correct_price(Decimal('9'), Decimal('10'))
    assert result.units == 0
    assert result.nano == 0
