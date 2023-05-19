from django.urls import path, register_converter
from .models import Players
from .serializers import PlayerSerializer
from rest_framework.generics import ListCreateAPIView
from . import views


urlpatterns = [
    path(
        'players/',
        ListCreateAPIView.as_view(
            queryset=Players.objects.all(),
            serializer_class=PlayerSerializer
        ),
        name='player-list'),
    path(
        'atpelo/',
        views.AtpEloList.as_view({"get": "list"})
        , name='atp-elo')
]
