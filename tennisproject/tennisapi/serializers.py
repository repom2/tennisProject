from rest_framework import serializers
from tennis_api.models import BetWta

from .models import AtpClayElo, AtpMatches, AtpTour, Bet, Players


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
        fields = "__all__"


class BetSerializer(serializers.Serializer):
    matchId = serializers.CharField(source="match_id")
    homeId = serializers.CharField(source="home_id")
    awayId = serializers.CharField(source="away_id")
    homeName = serializers.CharField(source="home_name")
    awayName = serializers.CharField(source="away_name")
    homeOdds = serializers.FloatField(source="home_odds")
    awayOdds = serializers.FloatField(source="away_odds")
    eloProbHard = serializers.FloatField(source="elo_prob_hard")
    eloProbClay = serializers.FloatField(source="elo_prob_clay")
    eloProbGrass = serializers.FloatField(source="elo_prob_grass")
    yearEloProb = serializers.FloatField(source="year_elo_prob")
    homeSpw = serializers.FloatField(source="home_spw")
    homeRpw = serializers.FloatField(source="home_rpw")
    awaySpw = serializers.FloatField(source="away_spw")
    awayRpw = serializers.FloatField(source="away_rpw")
    homeSpwClay = serializers.FloatField(source="home_spw_clay")
    homeRpwClay = serializers.FloatField(source="home_rpw_clay")
    awaySpwClay = serializers.FloatField(source="away_spw_clay")
    awayRpwClay = serializers.FloatField(source="away_rpw_clay")
    homeSpwGrass = serializers.FloatField(source="home_spw_grass")
    homeRpwGrass = serializers.FloatField(source="home_rpw_grass")
    awaySpwGrass = serializers.FloatField(source="away_spw_grass")
    awayRpwGrass = serializers.FloatField(source="away_rpw_grass")
    statsWin = serializers.FloatField(source="stats_win")
    statsWinHard = serializers.FloatField(source="stats_win_hard")
    statsWinClay = serializers.FloatField(source="stats_win_clay")
    statsWinGrass = serializers.FloatField(source="stats_win_grass")
    homeFatigue = serializers.FloatField(source="home_fatigue")
    awayFatigue = serializers.FloatField(source="away_fatigue")
    h2hWin = serializers.FloatField(source="h2h_win")
    h2hMatches = serializers.IntegerField(source="h2h_matches")
    walkover_home = serializers.BooleanField()
    walkover_away = serializers.BooleanField()
    homeInjScore = serializers.FloatField(source="home_inj_score")
    awayInjScore = serializers.FloatField(source="away_inj_score")
    commonOpponents = serializers.FloatField(source="common_opponents")
    commonOpponentsCount = serializers.IntegerField(source="common_opponents_count")
    preview = serializers.CharField()
    reasoning = serializers.CharField()
    startAt = serializers.DateTimeField(source="start_at")
    homeProb = serializers.FloatField(source="home_prob")
    awayProb = serializers.FloatField(source="away_prob")
    homeYield = serializers.FloatField(source="home_yield")
    awayYield = serializers.FloatField(source="away_yield")
    homeDr = serializers.FloatField(source="home_dr")
    awayDr = serializers.FloatField(source="away_dr")
    homeCurrentRank = serializers.IntegerField(source="home_current_rank")
    awayCurrentRank = serializers.IntegerField(source="away_current_rank")
    homePeakRank = serializers.CharField(source="home_peak_rank")
    awayPeakRank = serializers.CharField(source="away_peak_rank")
    homePlays = serializers.CharField(source="home_plays")
    awayPlays = serializers.CharField(source="away_plays")
    homeMatches = serializers.CharField(source="home_matches")
    awayMatches = serializers.CharField(source="away_matches")
    homeMatchesClay = serializers.CharField(source="home_matches_clay")
    awayMatchesClay = serializers.CharField(source="away_matches_clay")
    homeMatchesGrass = serializers.CharField(source="home_matches_grass")
    awayMatchesGrass = serializers.CharField(source="away_matches_grass")
    # homeStatMatches = serializers.IntegerField(source='home_stat_matches')
    # awayStatMatches = serializers.IntegerField(source='away_stat_matches')
    homePreview = serializers.CharField(source="home_preview")
    awayPreview = serializers.CharField(source="away_preview")
    homeShortPreview = serializers.CharField(source="home_short_preview")
    awayShortPreview = serializers.CharField(source="away_short_preview")
    homeTable = serializers.CharField(source="home_md_table")
    awayTable = serializers.CharField(source="away_md_table")
    homePlayerInfo = serializers.CharField(source="home_player_info")
    awayPlayerInfo = serializers.CharField(source="away_player_info")
    homeAH7_5 = serializers.FloatField(source="home_ah_7_5")
    homeAH6_5 = serializers.FloatField(source="home_ah_6_5")
    homeAH5_5 = serializers.FloatField(source="home_ah_5_5")
    homeAH4_5 = serializers.FloatField(source="home_ah_4_5")
    homeAH3_5 = serializers.FloatField(source="home_ah_3_5")
    homeAH2_5 = serializers.FloatField(source="home_ah_2_5")
    awayAH7_5 = serializers.FloatField(source="away_ah_7_5")
    awayAH6_5 = serializers.FloatField(source="away_ah_6_5")
    awayAH5_5 = serializers.FloatField(source="away_ah_5_5")
    awayAH4_5 = serializers.FloatField(source="away_ah_4_5")
    awayAH3_5 = serializers.FloatField(source="away_ah_3_5")
    awayAH2_5 = serializers.FloatField(source="away_ah_2_5")
    gamesOver21_5 = serializers.FloatField(source="games_over_21_5")
    gamesOver22_5 = serializers.FloatField(source="games_over_22_5")
    gamesOver23_5 = serializers.FloatField(source="games_over_23_5")
    gamesOver24_5 = serializers.FloatField(source="games_over_24_5")
    gamesOver25_5 = serializers.FloatField(source="games_over_25_5")
    homeWinSingleGame = serializers.FloatField(source="home_wins_single_game")
    homeWinSingleSet = serializers.FloatField(source="home_wins_single_set")
    homeWin1Set = serializers.FloatField(source="home_wins_1_set")
    homeWin2Set = serializers.FloatField(source="home_wins_2_set")
    awayWinSingleGame = serializers.FloatField(source="away_win_single_game")
    awayWinSingleSet = serializers.FloatField(source="away_win_single_set")
    awayWin1Set = serializers.FloatField(source="away_win_1_set")
    awayWin2Set = serializers.FloatField(source="away_win_2_set")
    surface = serializers.CharField()
    homeEloHard = serializers.FloatField(source="home_elo_hard")
    homeEloClay = serializers.FloatField(source="home_elo_clay")
    homeEloGrass = serializers.FloatField(source="home_elo_grass")
    awayEloHard = serializers.FloatField(source="away_elo_hard")
    awayEloClay = serializers.FloatField(source="away_elo_clay")
    awayEloGrass = serializers.FloatField(source="away_elo_grass")
    homeEloHardGames = serializers.FloatField(source="home_elo_hard_games")
    homeEloClayGames = serializers.FloatField(source="home_elo_clay_games")
    homeEloGrassGames = serializers.FloatField(source="home_elo_grass_games")
    awayEloHardGames = serializers.FloatField(source="away_elo_hard_games")
    awayEloClayGames = serializers.FloatField(source="away_elo_clay_games")
    awayEloGrassGames = serializers.FloatField(source="away_elo_grass_games")

    class Meta:
        model = BetWta
        fields = "__all__"


class AtptourSerializer(serializers.Serializer):
    class Meta:
        model = AtpTour
        fields = "__all__"


class AtpMatchesSerializer(serializers.Serializer):
    tour = AtptourSerializer(source="name", many=True, read_only=True)
    winner = PlayerSerializer(source="last_name", many=True, read_only=True)
    loser = PlayerSerializer(source="last_name", many=True, read_only=True)

    class Meta:
        model = AtpMatches
        fields = "__all__"


class AtpEloSerializer(serializers.Serializer):
    # match = AtpMatchesSerializer(many=True, read_only=True)
    slug = PlayerSerializer(many=True, read_only=True)
    twe = PlayerSerializer(source="last_name", many=True, read_only=True)
    elo = serializers.IntegerField()

    class Meta:
        model = AtpClayElo
        fields = ["elo", "slug__last_name", "twe"]
