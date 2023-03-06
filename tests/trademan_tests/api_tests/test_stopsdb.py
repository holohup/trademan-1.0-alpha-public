import pytest
from base.management.commands.stopsdb import (SHORT_BLACKLIST, STOP_BLACKLIST,
                                              WHITELIST)
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status


@pytest.mark.parametrize(
    ('stop_url', 'stop_list'),
    (
        ('stops-list', STOP_BLACKLIST),
        ('shorts-list', SHORT_BLACKLIST)
    )
)
@pytest.mark.django_db
def test_long_stops(client, db, django_db_setup, stop_url, stop_list):
    response = client.get(reverse(stop_url))
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []
    call_command('stopsdb')
    tickers = []
    response = client.get(reverse(stop_url))
    assert response.status_code == status.HTTP_200_OK
    for item in response.data:
        tickers.append(item['ticker'])
    for ticker in stop_list:
        assert ticker not in tickers
    for ticker in set(WHITELIST) - set(stop_list):
        assert ticker in tickers
