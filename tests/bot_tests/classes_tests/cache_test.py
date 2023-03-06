from decimal import Decimal, getcontext
from random import randint

import pytest

from bot.tools.cache import OrdersCache

getcontext().prec = 10


@pytest.fixture
def cache_preset():
    return OrdersCache(100, Decimal('50'))


@pytest.fixture
def filled_cache():
    cache = OrdersCache(50, Decimal('50'))
    cache.update('second', 200, Decimal('200'))
    cache.update('third', 300, Decimal('300'))
    return cache


def test_empty_cache():
    empty = OrdersCache()
    assert empty.amount == 0
    assert empty.avg_price == Decimal('0')
    assert empty.items == {}


@pytest.mark.parametrize(
    'error_values',
    (
        ('a', 0),
        (0, 0),
    )
)
def test_incorrect_init(error_values):
    with pytest.raises(ValueError):
        OrdersCache(*error_values)


def test_correct_init(cache_preset):
    retrieved = cache_preset.items['initial']
    assert retrieved.amount == 100
    assert retrieved.price == Decimal('50')


def test_correct_update_add_new(cache_preset):
    cache_preset.update('second', 200, Decimal('30'))
    retrieved = cache_preset.items['second']
    assert retrieved.amount == 200
    assert retrieved.price == Decimal('30')


def test_correct_update_existing(cache_preset):
    cache_preset.update('initial', 200, Decimal('30'))
    retrieved = cache_preset.items['initial']
    assert retrieved.amount == 200
    assert retrieved.price == Decimal('30')


def test_correct_average(filled_cache: OrdersCache):
    avg = filled_cache.avg_price
    assert isinstance(avg, Decimal)
    assert avg == Decimal('240.9090909')


def test_correct_sum(filled_cache: OrdersCache):
    sum = filled_cache.amount
    assert isinstance(sum, int)
    assert sum == 550


def test_price_by_id(filled_cache: OrdersCache):
    assert filled_cache.price_by_id('initial') == Decimal('50')
    assert filled_cache.price_by_id('second') == Decimal('200')
    assert filled_cache.price_by_id('third') == Decimal('300')
    assert filled_cache.price_by_id('non_existant') == 0


def test_executed_by_id(cache_preset: OrdersCache):
    amount = randint(1, 100)
    id = str(randint(100000, 200000))
    cache_preset.update(id, amount, Decimal(randint(50, 100)))
    assert cache_preset.executed_by_id(id) == amount


def test_non_existing_order_id_amount(cache_preset: OrdersCache):
    assert cache_preset.executed_by_id('non_existing') == 0
