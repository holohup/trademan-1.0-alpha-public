import pytest
from base.management.commands.stopsdb import (SHORT_BLACKLIST, STOP_BLACKLIST,
                                              WHITELIST)
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_long_stops(client, db, django_db_setup):
    response = client.get(reverse('stops-list'))
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []
    call_command('stopsdb')
    tickers = []
    response = client.get(reverse('stops-list'))
    assert response.status_code == status.HTTP_200_OK
    for item in response.data:
        tickers.append(item['ticker'])
    for ticker in STOP_BLACKLIST:
        assert ticker not in tickers
    for ticker in set(WHITELIST) - set(STOP_BLACKLIST):
        assert ticker in tickers


@pytest.mark.django_db
def test_short_stops(client, db, django_db_setup):
    response = client.get(reverse('shorts-list'))
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []
    call_command('stopsdb')
    tickers = []
    response = client.get(reverse('shorts-list'))
    for item in response.data:
        tickers.append(item['ticker'])
    for ticker in SHORT_BLACKLIST:
        assert ticker not in tickers
    for ticker in set(WHITELIST) - set(SHORT_BLACKLIST):
        assert ticker in tickers
