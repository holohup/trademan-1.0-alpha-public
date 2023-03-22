from decimal import Decimal

import pytest
from api.v1.stop_orders import TinkoffStopOrderAdapter
from base.models import StopOrder
from django.urls import reverse
from rest_framework import status
from tinkoff.invest.schemas import StopOrderDirection as SoD
from tinkoff.invest.utils import quotation_to_decimal


@pytest.fixture
def patched_get_response(client, sample_stop_orders_response, monkeypatch):
    def filled_response(self):
        return sample_stop_orders_response

    monkeypatch.setattr(
        TinkoffStopOrderAdapter, '_get_stop_orders', filled_response
    )
    return client.get(reverse('stop_orders'))


@pytest.mark.django_db
def test_not_empty_response_returns_right_status_code(patched_get_response):
    assert patched_get_response.status_code == status.HTTP_200_OK


def test_empty_get_response_returns_correct_error(
    client, sample_empty_stop_orders_response, monkeypatch
):
    def empty_response(self):
        return sample_empty_stop_orders_response

    monkeypatch.setattr(
        TinkoffStopOrderAdapter, '_get_stop_orders', empty_response
    )
    assert (
        client.get(reverse('stop_orders')).status_code
        == status.HTTP_404_NOT_FOUND
    )


@pytest.mark.django_db
def test_correct_number_of_objects_created(patched_get_response):
    assert StopOrder.objects.count() == 6


@pytest.mark.django_db
def test_correct_objects_created(
    patched_get_response, sample_stop_orders_response
):
    for order in sample_stop_orders_response:
        assert (
            StopOrder.objects.filter(
                asset__figi=order.figi,
                lots=order.lots_requested,
                order_type=order.order_type,
                stop_price=quotation_to_decimal(order.stop_price),
                price=quotation_to_decimal(order.price),
                sell=(order.direction == SoD.STOP_ORDER_DIRECTION_SELL),
            ).count()
            == 1
        )


@pytest.mark.django_db
def test_correct_response_without_stashed_orders(client):
    response = client.post(reverse('stop_orders'))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_correct_instrument_prices_will_be_passed(
    patched_get_response, sample_stop_orders_response
):
    adapter = TinkoffStopOrderAdapter('000', '000', '000')
    orders = StopOrder.objects.all()
    for order in orders:
        params = adapter._prepare_order_params(order)
        if order.asset.asset_type == 'B':
            assert quotation_to_decimal(
                params['price']
            ) == order.price / Decimal('10')
            assert quotation_to_decimal(
                params['stop_price']
            ) == order.stop_price / Decimal('10')
        else:
            assert quotation_to_decimal(params['price']) == order.price
            assert (
                quotation_to_decimal(params['stop_price']) == order.stop_price
            )
