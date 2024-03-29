from .models import AtpElo, AtpMatches, AtpTour, Players, Bet
from tennis_api.models import BetWta
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


class BetSerializer(serializers.Serializer):
    matchId = serializers.CharField(source='match_id')
    homeId = serializers.CharField(source='home_id')
    awayId = serializers.CharField(source='away_id')
    homeName = serializers.CharField(source='home_name')
    awayName = serializers.CharField(source='away_name')
    homeOdds = serializers.FloatField(source='home_odds')
    awayOdds = serializers.FloatField(source='away_odds')
    eloProb = serializers.FloatField(source='elo_prob')
    yearEloProb = serializers.FloatField(source='year_elo_prob')
    homeSpw = serializers.FloatField(source='home_spw')
    homeRpw = serializers.FloatField(source='home_rpw')
    awaySpw = serializers.FloatField(source='away_spw')
    awayRpw = serializers.FloatField(source='away_rpw')
    statsWin = serializers.FloatField(source='stats_win')
    homeFatigue = serializers.FloatField(source='home_fatigue')
    awayFatigue = serializers.FloatField(source='away_fatigue')
    h2hWin = serializers.FloatField(source='h2h_win')
    h2hMatches = serializers.IntegerField(source='h2h_matches')
    walkover_home = serializers.BooleanField()
    walkover_away = serializers.BooleanField()
    homeInjScore = serializers.FloatField(source='home_inj_score')
    awayInjScore = serializers.FloatField(source='away_inj_score')
    commonOpponents = serializers.FloatField(source='common_opponents')
    commonOpponentsCount = serializers.IntegerField(source='common_opponents_count')
    preview = serializers.CharField()
    reasoning = serializers.CharField()
    startAt = serializers.DateTimeField(source='start_at')
    homeProb = serializers.FloatField(source='home_prob')
    awayProb = serializers.FloatField(source='away_prob')
    homeYield = serializers.FloatField(source='home_yield')
    awayYield = serializers.FloatField(source='away_yield')
    homeDr = serializers.FloatField(source='home_dr')
    awayDr = serializers.FloatField(source='away_dr')
    homeCurrentRank = serializers.IntegerField(source='home_current_rank')
    awayCurrentRank = serializers.IntegerField(source='away_current_rank')
    homePeakRank = serializers.CharField(source='home_peak_rank')
    awayPeakRank = serializers.CharField(source='away_peak_rank')
    homePlays = serializers.CharField(source='home_plays')
    awayPlays = serializers.CharField(source='away_plays')
    homeMatches = serializers.CharField(source='home_matches')
    awayMatches = serializers.CharField(source='away_matches')
    #homeStatMatches = serializers.IntegerField(source='home_stat_matches')
    #awayStatMatches = serializers.IntegerField(source='away_stat_matches')
    homePreview = serializers.CharField(source='home_preview')
    awayPreview = serializers.CharField(source='away_preview')
    homeShortPreview = serializers.CharField(source='home_short_preview')
    awayShortPreview = serializers.CharField(source='away_short_preview')
    homeTable = serializers.CharField(source='home_md_table')
    awayTable = serializers.CharField(source='away_md_table')
    homePlayerInfo = serializers.CharField(source='home_player_info')
    awayPlayerInfo = serializers.CharField(source='away_player_info')
    homeAH7_5 = models.FloatField(source='home_ah_7_5')
    homeAH6_5 = models.FloatField(source='home_ah_6_5')
    homeAH5_5 = models.FloatField(source='home_ah_5_5')
    homeAH4_5 = models.FloatField(source='home_ah_4_5')
    homeAH3_5 = models.FloatField(source='home_ah_3_5')
    homeAH2_5 = models.FloatField(source='home_ah_2_5')
    awayAH7_5 = models.FloatField(source='away_ah_7_5')
    awayAH6_5 = models.FloatField(source='away_ah_6_5')
    awayAH5_5 = models.FloatField(source='away_ah_5_5')
    awayAH4_5 = models.FloatField(source='away_ah_4_5')
    awayAH3_5 = models.FloatField(source='away_ah_3_5')
    awayAH2_5 = models.FloatField(source='away_ah_2_5')
    gamesOver21_5 = models.FloatField(source='games_over_21_5')
    gamesOver22_5 = models.FloatField(source='games_over_22_5')
    gamesOver23_5 = models.FloatField(source='games_over_23_5')
    gamesOver24_5 = models.FloatField(source='games_over_24_5')
    gamesOver25_5 = models.FloatField(source='games_over_25_5')
    homeWinSingleGame = models.FloatField(source='homeWins_single_game')
    homeWinSingleSet = models.FloatField(source='homeWins_single_set')
    homeWin1Set = models.FloatField(source='homeWins_1_set')
    homeWin2Set = models.FloatField(source='homeWins_2_set')
    awayWinSingleGame = models.FloatField(source='awayWin_single_game')
    awayWinSingleSet = models.FloatField(source='awayWin_single_set')
    awayWin1Set = models.FloatField(source='awayWin_1_set')
    awayWin2Set = models.FloatField(source='away_win_2_set')


    class Meta:
        model = BetWta
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