import pytest
from base.models import Figi
from django.core.management import call_command


@pytest.mark.django_db
def test_db_is_not_empty():
    assert Figi.objects.count() > 0


@pytest.mark.django_db
def test_fixtures_not_in_db(api_fixtures):
    for inst in api_fixtures.keys():
        for fixture in api_fixtures[inst].instruments:
            assert Figi.objects.filter(figi=fixture.figi).count() == 0


@pytest.mark.django_db
def test_update_adds_corresponding_objects(monkeypatch, api_fixtures):
    monkeypatch.setattr(
        'base.management.commands.update.get_api_response',
        lambda x: api_fixtures[x],
    )
    call_command('update')
    for inst in api_fixtures.keys():
        for fixture in api_fixtures[inst].instruments:
            assert (Figi.objects.filter(
                figi=fixture.figi,
                ticker=fixture.ticker,
                lot=fixture.lot,
                name=fixture.name,
            ).count() == 1
            )
