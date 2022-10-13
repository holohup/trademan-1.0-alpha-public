from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StopsViewSet, ShortsViewSet, SellBuyViewSet, SpreadsViewSet, RestoreStopsViewSet, health

v1_router = DefaultRouter()
v1_router.register('stops', StopsViewSet, basename='stops')
v1_router.register('shorts', ShortsViewSet, basename='shorts')
v1_router.register('sellbuy', SellBuyViewSet, basename='sellbuy')
v1_router.register('spreads', SpreadsViewSet, basename='spreads')
v1_router.register('restorestops', RestoreStopsViewSet, basename='restorestops')

urlpatterns = [
    path('health/', health, name='health'),
    path('', include(v1_router.urls)),
]
