from django.urls import path, include

from rest_framework import routers

from profiles.api import views

ROUTER = routers.DefaultRouter()
ROUTER.register('countries', views.RepresentedCountriesViewSet)
ROUTER.register('positions', views.TopPositionsViewSet)

urlpatterns = [
    path('', include(ROUTER.urls)),
]