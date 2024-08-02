import logging

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db.models import F, Max, OuterRef, Subquery
from django.db.models.functions import Greatest
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from psycopg2.extensions import AsIs
from rest_framework import generics, viewsets
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from tennisapi.models import Bet, BetWta
from tennisapi.stats.player_stats import player_stats, match_stats

from .models import AtpElo, AtpHardElo, AtpTour, Bet, BetWta
from .serializers import AtpEloSerializer, BetSerializer
from tennisapi.stats.avg_swp_rpw_by_event import event_stats
from tennisapi.stats.prob_by_serve.winning_match import match_prob, matchProb

log = logging.getLogger(__name__)


class AtpEloList(generics.ListAPIView):
    queryset = AtpHardElo.objects.all()
    serializer_class = AtpEloSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAdminUser]

    def list(self, request):
        now = timezone.now()
        year_ago = now - relativedelta(days=180)

        players = (
            self.get_queryset()
            .filter(date__range=(year_ago, now))
            .values(
                "player_id",
                "elo",
                "games",
                "player__last_name",
                "player__first_name",
                "date",
            )
            .order_by("-elo")
        )

        max_date_elo_by_player = {}
        data = []
        for player in players:
            if player["player_id"] not in max_date_elo_by_player:
                max_date_elo_by_player[player["player_id"]] = player["elo"]
                player_data = {
                    "id": player["player_id"],
                    "first_name": player["player__first_name"],
                    "last_name": player["player__last_name"],
                    "latest_date": player["date"],
                    "elo": player["elo"],
                }
                data.append(player_data)

        return Response(data)


class BetList(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAdminUser]

    def list(self, request):
        # Get the level parameter from the URL query string
        level = request.GET.get("level", None)

        # Define your default queryset which will be used if 'level' is not 'wta'
        queryset = Bet.objects.all()

        # Change the queryset if 'level' is 'wta'
        if level == "wta":
            queryset = BetWta.objects.all()
        now = timezone.now()
        from_date = now - relativedelta(hours=55)
        queryset = queryset.filter(start_at__gte=from_date).order_by("start_at")
        queryset = queryset.annotate(
            max_value=Greatest(F("home_yield"), F("away_yield"))
        ).order_by("-max_value")
        serializer = BetSerializer(queryset, many=True)
        return Response(serializer.data)


class PlayerStatistics(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAdminUser]

    def list(self, request):
        # Get the level parameter from the URL query string
        now = timezone.now()
        start_at = now - relativedelta(days=365)
        level = request.GET.get("level", "atp")
        player_id = request.GET.get("playerId", "63bb0df01198c882a8c730abba4160d4")
        if level == "atp":
            matches_table = "tennisapi_atpmatches"
            hard_elo = "tennisapi_atphardelo"
            grass_elo = "tennisapi_atpgrasselo"
            clay_elo = "tennisapi_atpelo"
        elif level == "wta":
            matches_table = "tennisapi_wtamatches"
            hard_elo = "tennisapi_wtahardelo"
            grass_elo = "tennisapi_wtagrasselo"
            clay_elo = "tennisapi_wtaelo"
        else:
            raise Http404

        stats_params = {
            "limit": request.GET.get("limit", 5),
            "start_at": request.GET.get("start_at", start_at),
            "surface": AsIs(request.GET.get("surface", "Hard")),
            "matches_table": AsIs(matches_table),
            "hard_elo": AsIs(hard_elo),
            "grass_elo": AsIs(grass_elo),
            "clay_elo": AsIs(clay_elo),
        }
        player_spw, player_rpw, player_matches = player_stats(
            player_id, start_at, stats_params
        )

        matches = match_stats(player_id, start_at, stats_params)

        # pandas DataFrame to JSON
        #matches = matches.to_json(orient="records")

        content = {
            "playerSPW": player_spw,
            "playerRPW": player_rpw,
            "playerMatches": player_matches,
            "matches": matches,
        }
        return Response(content)


class MatchProbability(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAdminUser]

    def list(self, request):
        # Get the level parameter from the URL query string
        now = timezone.now()
        start_at = now - relativedelta(days=365)
        level = request.GET.get("level", "atp")
        player_id = request.GET.get("playerId", "63bb0df01198c882a8c730abba4160d4")
        if level == "atp":
            matches_table = "tennisapi_atpmatches"
            hard_elo = "tennisapi_atphardelo"
            grass_elo = "tennisapi_atpgrasselo"
            clay_elo = "tennisapi_atpelo"
        elif level == "wta":
            matches_table = "tennisapi_wtamatches"
            hard_elo = "tennisapi_wtahardelo"
            grass_elo = "tennisapi_wtagrasselo"
            clay_elo = "tennisapi_wtaelo"
        else:
            raise Http404

        tour_name = request.GET.get("tour", "olympics")
        home_spw = request.GET.get("homeSPW", 0.72)
        away_spw = request.GET.get("awaySPW", 0.68)
        home_rpw = request.GET.get("homeRPW", 0.49)
        away_rpw = request.GET.get("awayRPW", 0.42)
        params = {
            "limit": request.GET.get("limit", 5),
            "start_at": request.GET.get("start_at", start_at),
            "surface": AsIs(request.GET.get("surface", "Hard")),
            "matches_table": AsIs(matches_table),
            "hard_elo": AsIs(hard_elo),
            "grass_elo": AsIs(grass_elo),
            "clay_elo": AsIs(clay_elo),
            "event": AsIs(tour_name),
            "date": "2015-1-1",
        }
        event_spw, event_rpw, tour_spw, tour_rpw = event_stats(params, level)

        home_spw = tour_spw + (home_spw - tour_spw) - (away_rpw - tour_rpw)
        away_spw = tour_spw + (away_spw - tour_spw) - (home_rpw - tour_rpw)

        match_prob = matchProb(
            home_spw,
            1 - away_spw,
            gv=0,
            gw=0,
            sv=0,
            sw=0,
            mv=0,
            mw=0,
            sets=3,
        )

        content = {
            "eventSPW": event_spw,
            "eventRPW": event_rpw,
            "tourSPW": tour_spw,
            "tourRPW": tour_rpw,
            "matchProb": round(match_prob, 2),
        }

        return Response(content)
