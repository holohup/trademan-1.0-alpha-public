import pytest
from tinkoff.invest.schemas import FuturesResponse

from bot.scanner.scanner import ResponseFilter


def test_response_filter_raises_errors(futures_response):
    with pytest.raises(KeyError):
        ResponseFilter(futures_response.instruments)
    with pytest.raises(ValueError):
        ResponseFilter(FuturesResponse((0, 0)))
    with pytest.raises(ValueError):
        ResponseFilter(FuturesResponse())


def tests_instruments_get_basic_filtered(futures_response):
    filter = ResponseFilter(futures_response)
    assert len(filter._apply_basic_filter()) == 2
