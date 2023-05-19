from .models import AtpElo, AtpMatches, AtpTour, Players
from rest_framework import serializers


class PlayerSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    dob = serializers.DateField()
    hand = serializers.CharField()
    height = serializers.IntegerField()
    slug = serializers.CharField()
    country = serializers.CharField()
    prize_total_euros = serializers.IntegerField()

    class Meta:
        model = Players
        fields = '__all__'


class AtptourSerializer(serializers.Serializer):
    class Meta:
        model = AtpTour
        fields = '__all__'


class AtpMatchesSerializer(serializers.Serializer):
    tour = AtptourSerializer(source='name', many=True, read_only=True)
    winner = PlayerSerializer(source='last_name', many=True, read_only=True)
    loser = PlayerSerializer(source='last_name', many=True, read_only=True)

    class Meta:
        model = AtpMatches
        fields = '__all__'


class AtpEloSerializer(serializers.Serializer):
    #match = AtpMatchesSerializer(many=True, read_only=True)
    slug = PlayerSerializer(many=True, read_only=True)
    twe = PlayerSerializer(source='last_name', many=True, read_only=True)
    elo = serializers.IntegerField()

    class Meta:
        model = AtpElo
        fields = ['elo', 'slug__last_name', 'twe']