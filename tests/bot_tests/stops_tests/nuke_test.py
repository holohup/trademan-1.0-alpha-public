import pytest

from bot.place_stops import sum_is_valid
from bot.tools.utils import SellBuyCommand, parse_ticker_int_args


def test_parse_nuke_command_with_sum():
    assert parse_ticker_int_args('gazp 10000') == SellBuyCommand(
        'gazp', sum=10000
    )


def test_parse_nuke_command_with_amount():
    assert parse_ticker_int_args('100 gzm3') == SellBuyCommand('gzm3', 100)


def test_parse_nuke_command_with_just_a_ticker():
    assert parse_ticker_int_args('ngmk') == SellBuyCommand('ngmk')


@pytest.mark.parametrize(
    'invalid_input',
    (
        ('gazp gazp'), ('123 aaa 132')
    )
)
def test_correct_exception_is_raised(invalid_input):
    with pytest.raises(ValueError):
        parse_ticker_int_args(invalid_input)


def test_process_nuke_command_with_low_sum(sample_far_leg):
    assert sum_is_valid(sample_far_leg, 100) is False
