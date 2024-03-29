from decimal import Decimal

import pytest
from base.management.commands.update import INSTRUMENTS
from base.models import Figi, SellBuy, Spread, SpreadStats
from django.core.management import call_command
from tinkoff.invest.schemas import (Bond, BondsResponse, Future,
                                    FuturesResponse, MoneyValue, Quotation,
                                    Share, SharesResponse)


@pytest.fixture
def sellbuy_data(near_leg_sample):
    return {
        'active': True,
        'asset': near_leg_sample,
        'sell': False,
        'amount': 1000,
        'executed': 100,
        'avg_exec_price': Decimal('159.99'),
    }


@pytest.fixture
def sellbuy_sample(sellbuy_data):
    sellbuy = SellBuy(**sellbuy_data)
    sellbuy.save()
    return sellbuy


@pytest.fixture
def far_leg_data():
    return dict(
        figi='TGZZ.1',
        ticker='TGAZP',
        name='Gazprom',
        lot=10,
        min_price_increment=Decimal('1.0'),
        asset_type='F',
        api_trading_available=True,
        short_enabled=True,
        buy_enabled=True,
        sell_enabled=True,
        basic_asset_size=100,
        basic_asset='TGAZP2',
        morning_trading=True,
        evening_trading=True,
    )


@pytest.fixture
def near_leg_data():
    return dict(
        figi='TGZZ.2',
        ticker='TGAZP2',
        name='Gazprom',
        lot=10,
        min_price_increment=1,
        asset_type='S',
        api_trading_available=True,
        short_enabled=True,
        buy_enabled=True,
        sell_enabled=True,
        morning_trading=False,
        evening_trading=False,
    )


@pytest.fixture
def far_leg_sample(far_leg_data):
    far_leg = Figi(**far_leg_data)
    far_leg.save()
    return far_leg


@pytest.fixture
def near_leg_sample(near_leg_data):
    near_leg = Figi(**near_leg_data)
    near_leg.save()
    return near_leg


@pytest.fixture
def sample_spread(near_leg_sample, far_leg_sample):
    stats = SpreadStats.objects.create()
    return Spread.objects.create(
        far_leg=far_leg_sample,
        near_leg=near_leg_sample,
        price=0,
        sell=True,
        amount=10,
        stats=stats,
    )


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/trademan_tests/fixtures/figi.json')


@pytest.fixture
def api_fixtures():
    future = Future(
        basic_asset_size=Quotation(units=100, nano=0),
        figi='FUFUFU',
        ticker='fufufu',
        lot=1,
        name='FUTURE',
        min_price_increment=Quotation(units=1, nano=0),
        api_trade_available_flag=True,
        short_enabled_flag=True,
        buy_available_flag=True,
        sell_available_flag=True,
        real_exchange=INSTRUMENTS['Futures'].exchange,
    )
    share = Share(
        figi='SHSHSH',
        ticker='shshsh',
        lot=10,
        name='SHARE',
        min_price_increment=Quotation(units=0, nano=1000),
        api_trade_available_flag=True,
        short_enabled_flag=True,
        buy_available_flag=True,
        sell_available_flag=True,
        real_exchange=INSTRUMENTS['Stocks'].exchange,
    )
    bond = Bond(
        figi='BbBb',
        ticker='BbBb',
        lot=1,
        name='BOND',
        min_price_increment=Quotation(units=0, nano=1000),
        api_trade_available_flag=True,
        short_enabled_flag=True,
        buy_available_flag=True,
        sell_available_flag=True,
        real_exchange=INSTRUMENTS['Bonds'].exchange,
        nominal=MoneyValue(currency='rub', units=1000, nano=0),
    )
    return {
        'Futures': FuturesResponse(instruments=[future]),
        'Stocks': SharesResponse(instruments=[share]),
        'Bonds': BondsResponse(instruments=[bond]),
    }
