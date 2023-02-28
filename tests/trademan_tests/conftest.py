import pytest
from base.management.commands.update import INSTRUMENTS
from base.models import Figi, Spread
from django.core.management import call_command
from tinkoff.invest.schemas import (Future, FuturesResponse, Quotation, Share,
                                    SharesResponse)


@pytest.fixture
def far_leg_data():
    return dict(
        figi='TGZZ.1',
        ticker='TGAZP',
        name='Gazprom',
        lot=10,
        min_price_increment=1,
        type='F',
        api_trading_available=True,
        short_enabled=True,
        buy_enabled=True,
        sell_enabled=True,
        basic_asset_size=10,
    )


@pytest.fixture
def near_leg_data():
    return dict(
        figi='TGZZ.2',
        ticker='TGAZP2',
        name='Gazprom',
        lot=10,
        min_price_increment=1,
        type='S',
        api_trading_available=True,
        short_enabled=True,
        buy_enabled=True,
        sell_enabled=True,
        basic_asset_size=10,
    )


@pytest.fixture
def sample_spread(near_leg_data, far_leg_data):
    far_leg_figi = Figi(**far_leg_data)
    far_leg_figi.save()
    near_leg_figi = Figi(**near_leg_data)
    near_leg_figi.save()
    return Spread.objects.create(
        asset=far_leg_figi,
        near_leg=near_leg_figi,
        exec_price=0,
        price=0,
        sell=True,
        amount=10,
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
    return {
        'Futures': FuturesResponse(instruments=[future]),
        'Stocks': SharesResponse(instruments=[share])
    }
