from decimal import Decimal

import pytest
from base.models import Figi

both_sessions = pytest.mark.parametrize(
    'trading_session', (('morning_trading'), ('evening_trading'))
)


@pytest.fixture
def generic_asset_preset():
    return dict(
        ticker='BBB',
        name='CCC',
        lot=10,
        min_price_increment=Decimal('0.1'),
        api_trading_available=True,
        short_enabled=True,
        buy_enabled=True,
        sell_enabled=True,
    )


@pytest.fixture
def stock_preset(generic_asset_preset):
    stock = Figi(**{**generic_asset_preset, **{'type': 'S', 'figi': 'AAA'}})
    stock.save()
    return stock


@pytest.fixture
def future_preset(generic_asset_preset):
    future = Figi(
        **{
            **generic_asset_preset,
            **{'type': 'F', 'figi': 'BBB', 'basic_asset_size': 100},
        }
    )
    future.save()
    return future


@both_sessions
@pytest.mark.django_db
def test_morning_and_evening_trading_exists(
    stock_preset, future_preset, trading_session
):
    assert hasattr(stock_preset, trading_session)
    assert hasattr(future_preset, trading_session)


@both_sessions
@pytest.mark.django_db
def test_futures_default_sessions_are_set(future_preset, trading_session):
    future_preset.save()
    assert getattr(future_preset, trading_session) is True


@both_sessions
@pytest.mark.django_db
def test_sessions_state_changes_work(
    future_preset, stock_preset, trading_session
):
    assert getattr(future_preset, trading_session) is True
    assert getattr(stock_preset, trading_session) is False
    setattr(future_preset, trading_session, False)
    setattr(stock_preset, trading_session, True)
    future_preset.save()
    stock_preset.save()
    assert getattr(future_preset, trading_session) is False
    assert getattr(stock_preset, trading_session) is True
