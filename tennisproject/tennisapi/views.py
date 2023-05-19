from django.shortcuts import render
from django.http import Http404
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AtpTour, AtpElo
from .serializers import AtpEloSerializer


class AtpEloList(generics.ListCreateAPIView):
    queryset = AtpElo.objects.all()
    serializer_class = AtpEloSerializer

    def list(self, request):
        # Note the use of `get_queryset()` instead of `self.queryset`
        queryset = self.get_queryset()
        serializer = AtpEloSerializer(queryset, many=True)
        return Response(serializer.data)
