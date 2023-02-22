from http import HTTPStatus

from base.models import RestoreStops, SellBuy, Spread, Stops
from django.http import HttpResponse
from rest_framework import viewsets

from .serializers import (RestoreStopsSerializer, SellBuySerializer,
                          SpreadsSerializer, StopsSerializer)


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


def health(request):
    return HttpResponse(status=HTTPStatus.OK)
