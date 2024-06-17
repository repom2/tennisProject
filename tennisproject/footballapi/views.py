from django.shortcuts import render
from .models import BetFootball
from .serializers import BetSerializer
from rest_framework import generics
from django.db.models.functions import Greatest
from django.utils import timezone
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from dateutil.relativedelta import relativedelta
from django.db.models import F
import logging
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

log = logging.getLogger(__name__)


class BetList(generics.ListAPIView):
    queryset = BetFootball.objects.all()

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAdminUser]

    def list(self, request):
        now = timezone.now()
        from_date = now - relativedelta(hours=25)
        queryset = self.get_queryset().filter(start_at__gte=from_date).order_by('start_at')
        queryset = queryset.annotate(
            max_value=Greatest(F('home_yield'), F('away_yield'), F('draw_yield'))
        ).order_by('-max_value')
        serializer = BetSerializer(queryset, many=True)
        return Response(serializer.data)
