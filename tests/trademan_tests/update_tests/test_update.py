import pytest
from base.models import Figi
from django.core.management import call_command


@pytest.mark.django_db
def test_db_is_not_empty():
    assert Figi.objects.count() > 0


@pytest.mark.django_db
def test_fixtures_not_in_db(future_fixtures, stock_fixtures):
    for fixture in future_fixtures.instruments:
        assert Figi.objects.filter(figi=fixture.figi).count() == 0
    for fixture in stock_fixtures.instruments:
        assert Figi.objects.filter(figi=fixture.figi).count() == 0


@pytest.mark.django_db
def test_fixtures_in_db_after_update(future_fixtures, stock_fixtures, mocker):
    mocker.patch(
        'base.management.commands.update.get_api_response',
        return_value=future_fixtures,
    )
    call_command('update')
    for fixture in future_fixtures.instruments:
        assert Figi.objects.filter(figi=fixture.figi).count() == 1
    # mocker.patch(
    #     'base.management.commands.update.get_api_response',
    #     return_value=stock_fixtures,
    # )
    # call_command('update')
    # for fixture in stock_fixtures.instruments:
    #     assert Figi.objects.filter(figi=fixture.figi).count() == 1
