from http import HTTPStatus

from api.v1.stop_orders import TinkoffStopOrderAdapter
from base.models import Figi, SellBuy, Spread, StopOrder, Stops
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (SellBuySerializer, SpreadsSerializer,
                          StopsSerializer, TickerSerializer)


class StopsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stops.objects.filter(
        whitelist=True, stop_blacklist=False
    ).select_related('asset')
    serializer_class = StopsSerializer


class ShortsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stops.objects.filter(
        whitelist=True, short_blacklist=False
    ).select_related('asset')
    serializer_class = StopsSerializer


class SellBuyViewSet(viewsets.ModelViewSet):
    queryset = SellBuy.objects.filter(active=True).select_related('asset')
    serializer_class = SellBuySerializer

    def perform_update(self, serializer):
        serializer.save(
            active=(
                self.get_object().amount
                - serializer.validated_data.get('executed')
                >= self.get_object().asset.lot
            )
        )

    def create(self, serializer):
        data = self.request.data
        asset = get_object_or_404(Figi, figi=data['figi'])
        sellbuy = SellBuy.objects.create(
            asset=asset, amount=data['amount'], sell=data['sell']
        )
        serialized = self.get_serializer(sellbuy)
        return Response(serialized.data, status=status.HTTP_201_CREATED)


class SpreadsViewSet(viewsets.ModelViewSet):
    queryset = (
        Spread.objects.filter(active=True)
        .select_related('far_leg', 'near_leg', 'stats')
        .order_by('id')
    )
    serializer_class = SpreadsSerializer


class StopOrdersView(APIView):
    def get(self, request):
        adapter = TinkoffStopOrderAdapter(
            settings.TCS_RO_TOKEN,
            settings.TCS_ACCOUNT_ID,
            settings.RETRY_SETTINGS,
        )
        response = adapter.get_stop_orders_params()
        if not response:
            return Response(
                'No active stop orders found.',
                status=status.HTTP_404_NOT_FOUND,
            )
        for item in response:
            figi = item.pop('figi')
            item['asset'], _ = Figi.objects.get_or_create(figi=figi)
        with transaction.atomic():
            StopOrder.objects.all().delete()
            StopOrder.objects.bulk_create(
                [StopOrder(**order) for order in response]
            )
        return Response('Active orders stashed.', status=status.HTTP_200_OK)

    def post(self, request):
        orders = StopOrder.objects.all()
        if orders.count() == 0:
            return Response(
                'No stop orders found in database.',
                status=status.HTTP_404_NOT_FOUND,
            )
        adapter = TinkoffStopOrderAdapter(
            settings.TCS_RW_TOKEN,
            settings.TCS_ACCOUNT_ID,
            settings.RETRY_SETTINGS,
        )
        adapter.place_stop_orders(orders)
        return Response('Stop orders restored', status=status.HTTP_200_OK)


class TickerViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Figi, ticker__iexact=kwargs['ticker'])
        return Response(TickerSerializer(instance).data)


def health(request):
    return HttpResponse(status=HTTPStatus.OK)
