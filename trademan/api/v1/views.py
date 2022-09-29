from .serializers import StopsSerializer
from base.models import Stops
from rest_framework import viewsets


class StopsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stops.objects.filter(whitelist=True, stop_blacklist=False)
    serializer_class = StopsSerializer


class ShortsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stops.objects.filter(whitelist=True, short_blacklist=False)
    serializer_class = StopsSerializer

