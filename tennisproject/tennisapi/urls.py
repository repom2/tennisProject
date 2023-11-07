from django.urls import path, register_converter
from .models import Players
from .serializers import PlayerSerializer
from rest_framework.generics import ListAPIView
from . import views


urlpatterns = [
    path(
        'players/',
        ListAPIView.as_view(
            queryset=Players.objects.all()[:1],
            serializer_class=PlayerSerializer
        ),
        name='player-list'),
    path(
        'atpelo/',
        views.AtpEloList.as_view()
        , name='atp-elo')
]
