from .models import AtpElo, AtpMatches, AtpTour, Players
from rest_framework import serializers


class PlayerSerializer(serializers.Serializer):
    class Meta:
        model = Players
        fields = '__all__'


class AtptourSerializer(serializers.Serializer):
    class Meta:
        model = AtpTour
        fields = '__all__'


class AtpMatchesSerializer(serializers.Serializer):
    winner = PlayerSerializer(many=True, read_only=True)
    loser = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = AtpMatches
        fields = '__all__'


class AtpEloSerializer(serializers.Serializer):
    match = AtpMatchesSerializer(many=True, read_only=True)
    player = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = AtpElo
        fields = '__all__'