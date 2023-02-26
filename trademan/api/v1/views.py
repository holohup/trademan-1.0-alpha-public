from http import HTTPStatus

from base.models import Figi, RestoreStops, SellBuy, Spread, Stops
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response

from .serializers import (RestoreStopsSerializer, SellBuySerializer,
                          SpreadsSerializer, StopsSerializer, TickerSerializer)


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


class SpreadsViewSet(viewsets.ModelViewSet):
    queryset = Spread.objects.filter(active=True).select_related('asset')
    serializer_class = SpreadsSerializer

    def perform_update(self, serializer):
        serializer.save(
            active=not serializer.validated_data.get('executed')
            >= self.get_object().amount
        )


class RestoreStopsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RestoreStops.objects.filter(active=True).select_related('asset')
    serializer_class = RestoreStopsSerializer


class TickerViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Figi, ticker__iexact=kwargs['ticker'])
        return Response(TickerSerializer(instance).data)


def health(request):
    return HttpResponse(status=HTTPStatus.OK)
