from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StopsViewSet, ShortsViewSet

v1_router = DefaultRouter()
v1_router.register('stops', StopsViewSet, basename='stops')
v1_router.register('shorts', ShortsViewSet, basename='shorts')

urlpatterns = [
    path('', include(v1_router.urls)),
]
