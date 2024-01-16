from django.shortcuts import render
from django.http import Http404
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Bet, AtpTour, AtpElo, AtpHardElo, BetWta
from .serializers import AtpEloSerializer, BetSerializer
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User
from rest_framework.permissions import IsAdminUser
from django.db.models import F, Max, Subquery, OuterRef
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import logging

log = logging.getLogger(__name__)


class AtpEloList(generics.ListAPIView):
    queryset = AtpHardElo.objects.all()
    serializer_class = AtpEloSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAdminUser]

    def list(self, request):
        now = timezone.now()
        year_ago = now - relativedelta(days=180)

        players = self.get_queryset().filter(date__range=(year_ago, now))\
            .values(
            'player_id',
            'elo',
            'games',
            'player__last_name',
            'player__first_name',
            'date'
        ).order_by('-elo')

        max_date_elo_by_player = {}
        data = []
        for player in players:
            if player['player_id'] not in max_date_elo_by_player:
                max_date_elo_by_player[player['player_id']] = player['elo']
                player_data = {
                    'id': player['player_id'],
                    'first_name': player['player__first_name'],
                    'last_name': player['player__last_name'],
                    'latest_date': player['date'],
                    'elo': player['elo']
                }
                data.append(player_data)

        return Response(data)


class BetList(generics.ListAPIView):
    queryset = BetWta.objects.all()

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAdminUser]

    def list(self, request):
        now = timezone.now()
        from_date = now# - relativedelta(days=1)
        queryset = self.get_queryset().filter(start_at__gte=from_date).order_by('start_at')
        log.info(f"queryset: {queryset}")
        serializer = BetSerializer(queryset, many=True)
        log.info(f"serializer: {serializer}")
        return Response(serializer.data)
