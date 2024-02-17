from django.urls import path, register_converter
from rest_framework.generics import ListAPIView
from . import views


urlpatterns = [
    path(
        'football-bet-list/',
        views.BetList.as_view()
        , name='football-bet-list'
    )
]
