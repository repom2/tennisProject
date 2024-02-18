from .models import BetFootball
from rest_framework import serializers


class BetSerializer(serializers.Serializer):
    matchId = serializers.CharField(source='id')
    homeId = serializers.CharField(source='home_id')
    awayId = serializers.CharField(source='away_id')
    homeName = serializers.CharField(source='home_name')
    awayName = serializers.CharField(source='away_name')
    homeOdds = serializers.FloatField(source='home_odds')
    drawOdds = serializers.FloatField(source='draw_odds')
    awayOdds = serializers.FloatField(source='away_odds')
    eloProb = serializers.FloatField(source='elo_prob')
    eloProbHome = serializers.FloatField(source='elo_prob_home')
    preview = serializers.CharField()
    reasoning = serializers.CharField()
    startAt = serializers.DateTimeField(source='start_at')
    homeProb = serializers.FloatField(source='home_prob')
    drawProb = serializers.FloatField(source='draw_prob')
    awayProb = serializers.FloatField(source='away_prob')
    homeYield = serializers.FloatField(source='home_yield')
    drawYield = serializers.FloatField(source='draw_yield')
    awayYield = serializers.FloatField(source='away_yield')

    class Meta:
        model = BetFootball
        fields = '__all__'
