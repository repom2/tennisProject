from django.urls import path, register_converter
from .models import Players
from .serializers import PlayerSerializer
from rest_framework.generics import ListAPIView
from . import views


urlpatterns = [
    path(
        "players/",
        ListAPIView.as_view(
            queryset=Players.objects.filter(sportscore_id__isnull=False)[:3],
            serializer_class=PlayerSerializer,
        ),
        name="player-list",
    ),
    path("atp-elo/", views.AtpEloList.as_view(), name="atp-elo"),
    path("bet-list/", views.BetList.as_view(), name="bet-list"),
    path("player-statistics/", views.PlayerStatistics.as_view(), name="player-statistics"),
]
