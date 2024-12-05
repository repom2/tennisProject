import logging
import pandas as pd

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db.models import F, Max, OuterRef, Subquery
from django.db.models.functions import Greatest
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone
from psycopg2.extensions import AsIs
from rest_framework import generics, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from tennisapi.models import Bet, BetWta
from tennisapi.stats.player_stats import player_stats, match_stats

from .models import AtpClayElo, AtpHardElo, AtpTour, Bet, BetWta
from .serializers import AtpEloSerializer, BetSerializer
from tennisapi.stats.avg_swp_rpw_by_event import event_stats
from tennisapi.stats.prob_by_serve.winning_match import match_prob, matchProb
from tennisapi.ml.utils import define_query_parameters

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
            clay_elo = "tennisapi_atpclayelo"
        elif level == "wta":
            matches_table = "tennisapi_wtamatches"
            hard_elo = "tennisapi_wtahardelo"
            grass_elo = "tennisapi_wtagrasselo"
            clay_elo = "tennisapi_wtaclayelo"
        else:
            raise Http404

        stats_params = {
            "limit": request.GET.get("limit", 7),
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
        # matches = matches.to_json(orient="records")

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
        if level == "atp":
            sets = 3
        else:
            sets = 3
        player_id = request.GET.get("playerId", "63bb0df01198c882a8c730abba4160d4")
        if level == "atp":
            matches_table = "tennisapi_atpmatches"
            hard_elo = "tennisapi_atphardelo"
            grass_elo = "tennisapi_atpgrasselo"
            clay_elo = "tennisapi_atpclayelo"
        elif level == "wta":
            matches_table = "tennisapi_wtamatches"
            hard_elo = "tennisapi_wtahardelo"
            grass_elo = "tennisapi_wtagrasselo"
            clay_elo = "tennisapi_wtaclayelo"
        else:
            raise Http404

        tour = request.GET.get("tour", level + "-final")

        home_spw = request.GET.get("homeSPW", 0.686)
        home_rpw = request.GET.get("homeRPW", 0.364)
        away_spw = request.GET.get("awaySPW", 0.703)
        away_rpw = request.GET.get("awayRPW", 0.414)
        end_at = now + relativedelta(days=3)
        params, match_qs, bet_qs, player_qs, surface = define_query_parameters(
            level, tour, now, end_at
        )

        event_spw, event_rpw, tour_spw, tour_rpw = event_stats(params, level)

        home_spw = tour_spw + (home_spw - tour_spw) - (away_rpw - tour_rpw)
        away_spw = tour_spw + (away_spw - tour_spw) - (home_rpw - tour_rpw)

        data = pd.DataFrame()
        data = match_prob(
            home_spw, 1 - away_spw, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=sets
        )

        log.info(data)
        win_prob = data["stats_win"]
        # replace nan with 0
        data = data.fillna(0)

        content = {
            "sets": sets,
            "eventSPW": event_spw,
            "eventRPW": event_rpw,
            "tourSPW": tour_spw,
            "tourRPW": tour_rpw,
            "matchProb": round(win_prob, 3),
            "homeWinsSingleGame": round(data["home_wins_single_game"], 3),
            "homeWinsSingleSet": round(data["home_wins_single_set"], 3),
            "homeWins1Set": round(data["home_wins_1_set"], 3),
            "home_ah_7_5": round(data["home_ah_7_5"], 3),
            "home_ah_6_5": round(data["home_ah_6_5"], 3),
            "home_ah_5_5": round(data["home_ah_5_5"], 3),
            "home_ah_4_5": round(data["home_ah_4_5"], 3),
            "home_ah_3_5": round(data["home_ah_3_5"], 3),
            "home_ah_2_5": round(data["home_ah_2_5"], 3),
            "games_over_21_5": round(data["games_over_21_5"], 3),
            "games_over_22_5": round(data["games_over_22_5"], 3),
            "games_over_23_5": round(data["games_over_23_5"], 3),
            "games_over_24_5": round(data["games_over_24_5"], 3),
            "games_over_25_5": round(data["games_over_25_5"], 3),
        }

        return Response(content)
