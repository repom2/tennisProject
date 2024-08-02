from django.db import models


class Players(models.Model):
    id = models.TextField(primary_key=True)
    sportscore_id = models.IntegerField(null=True)
    player_id = models.IntegerField(null=True)
    dob = models.DateField(null=True)
    hand = models.TextField(null=True)
    country_code = models.TextField(null=True)
    height = models.FloatField(null=True)
    wikidata_id = models.TextField(null=True)
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    slug = models.TextField(null=True)
    country = models.TextField(null=True)
    prize_total_euros = models.IntegerField(null=True)
    name_full = models.TextField(null=True)
    atp_name_full = models.TextField(null=True)


class WTAPlayers(models.Model):
    id = models.TextField(primary_key=True)
    sportscore_id = models.IntegerField(null=True)
    player_id = models.IntegerField(null=True)
    dob = models.DateField(null=True)
    hand = models.TextField(null=True)
    country_code = models.TextField(null=True)
    height = models.FloatField(null=True)
    wikidata_id = models.TextField(null=True)
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    slug = models.TextField(null=True)
    country = models.TextField(null=True)
    prize_total_euros = models.IntegerField(null=True)
    name_full = models.TextField(null=True)
    atp_name_full = models.TextField(null=True)


class AtpTour(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField(null=True)
    date = models.DateField(null=True)
    surface = models.TextField(null=True)


class ChTour(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField(null=True)
    date = models.DateField(null=True)
    surface = models.TextField(null=True)


class WtaTour(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField(null=True)
    date = models.DateField(null=True)
    surface = models.TextField(null=True)


class AtpElo(models.Model):
    match = models.ForeignKey(
        'AtpMatches',
        on_delete=models.DO_NOTHING,
        related_name="match",
    )
    player = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        related_name="player",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class AtpHardElo(models.Model):
    match = models.ForeignKey(
        'AtpMatches',
        on_delete=models.DO_NOTHING,
        related_name="hardmatch",
    )
    player = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        related_name="hardplayer",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class AtpGrassElo(models.Model):
    match = models.ForeignKey(
        'AtpMatches',
        on_delete=models.DO_NOTHING,
        related_name="grassmatch",
    )
    player = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        related_name="grassplayer",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class ChElo(models.Model):
    match = models.ForeignKey(
        'ChMatches',
        on_delete=models.DO_NOTHING,
        related_name="chmatch",
    )
    player = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        related_name="chplayer",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class WtaElo(models.Model):
    match = models.ForeignKey(
        'WtaMatches',
        on_delete=models.DO_NOTHING,
        related_name="wtamatch",
    )
    player = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        related_name="wtaplayer",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class WtaHardElo(models.Model):
    match = models.ForeignKey(
        'WtaMatches',
        on_delete=models.DO_NOTHING,
        related_name="wtahardmatch",
    )
    player = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        related_name="wtahardplayer",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class WtaGrassElo(models.Model):
    match = models.ForeignKey(
        'WtaMatches',
        on_delete=models.DO_NOTHING,
        related_name="wtagrassmatch",
    )
    player = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        related_name="wtagrassplayer",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class AtpMatches(models.Model):
    id = models.TextField(primary_key=True)
    tour_id = models.TextField(null=True)
    tourney_name = models.TextField(null=True)
    winner_name = models.TextField(null=True)
    loser_name = models.TextField(null=True)
    surface = models.TextField(null=True)
    winner = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="winners",
    )
    loser = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="losers",
    )
    date = models.DateField(null=True)
    round_name = models.TextField(null=True)
    match_num = models.IntegerField(null=True)
    court_time = models.IntegerField(null=True)
    w_ace = models.IntegerField(null=True)
    w_df = models.IntegerField(null=True)
    w_svpt = models.IntegerField(null=True)
    w_firstin = models.IntegerField(null=True)
    w_firstwon = models.IntegerField(null=True)
    w_secondwon = models.IntegerField(null=True)
    w_svgms = models.IntegerField(null=True)
    w_bpsaved = models.IntegerField(null=True)
    w_bpfaced = models.IntegerField(null=True)
    l_ace = models.IntegerField(null=True)
    l_df = models.IntegerField(null=True)
    l_svpt = models.IntegerField(null=True)
    l_firstin = models.IntegerField(null=True)
    l_firstwon = models.IntegerField(null=True)
    l_secondwon = models.IntegerField(null=True)
    l_svgms = models.IntegerField(null=True)
    l_bpsaved = models.IntegerField(null=True)
    l_bpfaced = models.IntegerField(null=True)
    event_id = models.TextField(null=True)
    winner_code = models.TextField(null=True)
    winner_service_points_won = models.IntegerField(null=True)
    winner_total_points = models.IntegerField(null=True)
    winner_receiver_points_won = models.IntegerField(null=True)
    loser_service_points_won = models.IntegerField(null=True)
    loser_total_points = models.IntegerField(null=True)
    loser_receiver_points_won = models.IntegerField(null=True)


class ChMatches(models.Model):
    id = models.TextField(primary_key=True)
    tour = models.ForeignKey(
        to=ChTour,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="chtours",
    )
    winner = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="chwinners",
    )
    loser = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="chlosers",
    )
    date = models.DateField(null=True)
    round_name = models.TextField(null=True)
    match_num = models.IntegerField(null=True)


class WtaMatches(models.Model):
    id = models.TextField(primary_key=True)
    tour_id = models.TextField(null=True)
    tourney_name = models.TextField(null=True)
    winner_name = models.TextField(null=True)
    loser_name = models.TextField(null=True)
    surface = models.TextField(null=True)
    winner = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="winners",
    )
    loser = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="losers",
    )
    date = models.DateField(null=True)
    round_name = models.TextField(null=True)
    match_num = models.IntegerField(null=True)
    court_time = models.IntegerField(null=True)
    w_ace = models.IntegerField(null=True)
    w_df = models.IntegerField(null=True)
    w_svpt = models.IntegerField(null=True)
    w_firstin = models.IntegerField(null=True)
    w_firstwon = models.IntegerField(null=True)
    w_secondwon = models.IntegerField(null=True)
    w_svgms = models.IntegerField(null=True)
    w_bpsaved = models.IntegerField(null=True)
    w_bpfaced = models.IntegerField(null=True)
    l_ace = models.IntegerField(null=True)
    l_df = models.IntegerField(null=True)
    l_svpt = models.IntegerField(null=True)
    l_firstin = models.IntegerField(null=True)
    l_firstwon = models.IntegerField(null=True)
    l_secondwon = models.IntegerField(null=True)
    l_svgms = models.IntegerField(null=True)
    l_bpsaved = models.IntegerField(null=True)
    l_bpfaced = models.IntegerField(null=True)
    event_id = models.TextField(null=True)
    winner_code = models.TextField(null=True)
    winner_service_points_won = models.IntegerField(null=True)
    winner_total_points = models.IntegerField(null=True)
    winner_receiver_points_won = models.IntegerField(null=True)
    loser_service_points_won = models.IntegerField(null=True)
    loser_total_points = models.IntegerField(null=True)
    loser_receiver_points_won = models.IntegerField(null=True)


class Match(models.Model):
    id = models.TextField(primary_key=True)
    tour_id = models.TextField(null=True)
    home = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="home",
    )
    away = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="away",
    )
    home_name = models.TextField(null=True)
    away_name = models.TextField(null=True)
    start_at = models.DateTimeField(null=True)
    round_name = models.TextField(null=True)
    match_num = models.IntegerField(null=True)
    home_odds = models.TextField(null=True)
    away_odds = models.TextField(null=True)
    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)
    winner_code = models.IntegerField(null=True)
    court_time = models.IntegerField(null=True)
    surface = models.TextField(null=True)
    tourney_name = models.TextField(null=True)


class ChMatch(models.Model):
    id = models.TextField(primary_key=True)
    tour = models.ForeignKey(
        to=ChTour,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="matches",
    )
    home = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="chhome",
    )
    away = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="chaway",
    )
    start_at = models.DateTimeField(null=True)
    round_name = models.TextField(null=True)
    match_num = models.IntegerField(null=True)
    home_odds = models.TextField(null=True)
    away_odds = models.TextField(null=True)
    winner_code = models.IntegerField(null=True)


class WtaMatch(models.Model):
    id = models.TextField(primary_key=True)
    tour_id = models.TextField(null=True)
    home = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="home",
    )
    away = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="away",
    )
    home_name = models.TextField(null=True)
    away_name = models.TextField(null=True)
    start_at = models.DateTimeField(null=True)
    round_name = models.TextField(null=True)
    match_num = models.IntegerField(null=True)
    home_odds = models.TextField(null=True)
    away_odds = models.TextField(null=True)
    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)
    winner_code = models.IntegerField(null=True)
    court_time = models.IntegerField(null=True)
    surface = models.TextField(null=True)
    tourney_name = models.TextField(null=True)


class Bet(models.Model):
    match = models.OneToOneField(
        Match, on_delete=models.CASCADE
    )
    home = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="homebet",
    )
    away = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="awaybet",
    )
    home_name = models.TextField(null=True)
    away_name = models.TextField(null=True)
    home_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    elo_prob = models.FloatField(null=True)
    elo_prob_clay = models.FloatField(null=True)
    elo_prob_grass = models.FloatField(null=True)
    year_elo_prob = models.FloatField(null=True)
    home_spw = models.FloatField(null=True)
    home_rpw = models.FloatField(null=True)
    away_spw = models.FloatField(null=True)
    away_rpw = models.FloatField(null=True)
    stats_win = models.FloatField(null=True)
    home_fatigue = models.FloatField(null=True)
    away_fatigue = models.FloatField(null=True)
    h2h_win = models.FloatField(null=True)
    h2h_matches = models.IntegerField(null=True)
    walkover_home = models.BooleanField(null=True)
    walkover_away = models.BooleanField(null=True)
    home_inj_score = models.FloatField(null=True)
    away_inj_score = models.FloatField(null=True)
    common_opponents = models.FloatField(null=True)
    common_opponents_count = models.IntegerField(null=True)
    preview = models.TextField(null=True)
    reasoning = models.TextField(null=True)
    start_at = models.DateTimeField(null=True)
    home_prob = models.FloatField(null=True)
    away_prob = models.FloatField(null=True)
    home_yield = models.FloatField(null=True)
    away_yield = models.FloatField(null=True)
    surface = models.TextField(null=True)
    home_dr = models.FloatField(null=True)
    away_dr = models.FloatField(null=True)
    home_matches = models.TextField(null=True)
    away_matches = models.TextField(null=True)
    home_peak_rank = models.TextField(null=True)
    away_peak_rank = models.TextField(null=True)
    home_current_rank = models.IntegerField(null=True)
    away_current_rank = models.IntegerField(null=True)
    home_plays = models.TextField(null=True)
    away_plays = models.TextField(null=True)
    home_player_info = models.TextField(null=True)
    away_player_info = models.TextField(null=True)
    home_md_table = models.TextField(null=True)
    away_md_table = models.TextField(null=True)
    home_preview = models.TextField(null=True)
    home_short_preview = models.TextField(null=True)
    away_preview = models.TextField(null=True)
    away_short_preview = models.TextField(null=True)
    home_ah_7_5 = models.FloatField(null=True)
    home_ah_6_5 = models.FloatField(null=True)
    home_ah_5_5 = models.FloatField(null=True)
    home_ah_4_5 = models.FloatField(null=True)
    home_ah_3_5 = models.FloatField(null=True)
    home_ah_2_5 = models.FloatField(null=True)
    away_ah_7_5 = models.FloatField(null=True)
    away_ah_6_5 = models.FloatField(null=True)
    away_ah_5_5 = models.FloatField(null=True)
    away_ah_4_5 = models.FloatField(null=True)
    away_ah_3_5 = models.FloatField(null=True)
    away_ah_2_5 = models.FloatField(null=True)
    games_over_21_5 = models.FloatField(null=True)
    games_over_22_5 = models.FloatField(null=True)
    games_over_23_5 = models.FloatField(null=True)
    games_over_24_5 = models.FloatField(null=True)
    games_over_25_5 = models.FloatField(null=True)
    home_wins_single_game = models.FloatField(null=True)
    home_wins_single_set = models.FloatField(null=True)
    home_wins_1_set = models.FloatField(null=True)
    home_wins_2_set = models.FloatField(null=True)
    away_win_single_game = models.FloatField(null=True)
    away_win_single_set = models.FloatField(null=True)
    away_win_1_set = models.FloatField(null=True)
    away_win_2_set = models.FloatField(null=True)
    home_spw_clay = models.FloatField(null=True)
    home_rpw_clay = models.FloatField(null=True)
    home_dr_clay = models.FloatField(null=True)
    home_matches_clay = models.TextField(null=True)
    away_spw_clay = models.FloatField(null=True)
    away_rpw_clay = models.FloatField(null=True)
    away_dr_clay = models.FloatField(null=True)
    away_matches_clay = models.TextField(null=True)
    stats_win_clay = models.FloatField(null=True)
    home_spw_grass = models.FloatField(null=True)
    home_rpw_grass = models.FloatField(null=True)
    home_dr_grass = models.FloatField(null=True)
    home_matches_grass = models.TextField(null=True)
    away_spw_grass = models.FloatField(null=True)
    away_rpw_grass = models.FloatField(null=True)
    away_dr_grass = models.FloatField(null=True)
    away_matches_grass = models.TextField(null=True)
    stats_win_grass = models.FloatField(null=True)


class BetWta(models.Model):
    match = models.OneToOneField(
        WtaMatch, on_delete=models.CASCADE
    )
    home = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="homebet",
    )
    away = models.ForeignKey(
        to=WTAPlayers,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="awaybet",
    )
    home_name = models.TextField(null=True)
    away_name = models.TextField(null=True)
    home_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    elo_prob = models.FloatField(null=True)
    elo_prob_clay = models.FloatField(null=True)
    elo_prob_grass = models.FloatField(null=True)
    year_elo_prob = models.FloatField(null=True)
    home_spw = models.FloatField(null=True)
    home_rpw = models.FloatField(null=True)
    away_spw = models.FloatField(null=True)
    away_rpw = models.FloatField(null=True)
    stats_win = models.FloatField(null=True)
    home_fatigue = models.FloatField(null=True)
    away_fatigue = models.FloatField(null=True)
    h2h_win = models.FloatField(null=True)
    h2h_matches = models.IntegerField(null=True)
    walkover_home = models.BooleanField(null=True)
    walkover_away = models.BooleanField(null=True)
    home_inj_score = models.FloatField(null=True)
    away_inj_score = models.FloatField(null=True)
    common_opponents = models.FloatField(null=True)
    common_opponents_count = models.IntegerField(null=True)
    preview = models.TextField(null=True)
    reasoning = models.TextField(null=True)
    start_at = models.DateTimeField(null=True)
    home_prob = models.FloatField(null=True)
    away_prob = models.FloatField(null=True)
    home_yield = models.FloatField(null=True)
    away_yield = models.FloatField(null=True)
    surface = models.TextField(null=True)
    home_dr = models.FloatField(null=True)
    away_dr = models.FloatField(null=True)
    home_matches = models.TextField(null=True)
    away_matches = models.TextField(null=True)
    home_peak_rank = models.TextField(null=True)
    away_peak_rank = models.TextField(null=True)
    home_current_rank = models.IntegerField(null=True)
    away_current_rank = models.IntegerField(null=True)
    home_plays = models.TextField(null=True)
    away_plays = models.TextField(null=True)
    home_player_info = models.TextField(null=True)
    away_player_info = models.TextField(null=True)
    home_md_table = models.TextField(null=True)
    away_md_table = models.TextField(null=True)
    home_preview = models.TextField(null=True)
    home_short_preview = models.TextField(null=True)
    away_preview = models.TextField(null=True)
    away_short_preview = models.TextField(null=True)
    home_ah_7_5 = models.FloatField(null=True)
    home_ah_6_5 = models.FloatField(null=True)
    home_ah_5_5 = models.FloatField(null=True)
    home_ah_4_5 = models.FloatField(null=True)
    home_ah_3_5 = models.FloatField(null=True)
    home_ah_2_5 = models.FloatField(null=True)
    away_ah_7_5 = models.FloatField(null=True)
    away_ah_6_5 = models.FloatField(null=True)
    away_ah_5_5 = models.FloatField(null=True)
    away_ah_4_5 = models.FloatField(null=True)
    away_ah_3_5 = models.FloatField(null=True)
    away_ah_2_5 = models.FloatField(null=True)
    games_over_21_5 = models.FloatField(null=True)
    games_over_22_5 = models.FloatField(null=True)
    games_over_23_5 = models.FloatField(null=True)
    games_over_24_5 = models.FloatField(null=True)
    games_over_25_5 = models.FloatField(null=True)
    home_wins_single_game = models.FloatField(null=True)
    home_wins_single_set = models.FloatField(null=True)
    home_wins_1_set = models.FloatField(null=True)
    home_wins_2_set = models.FloatField(null=True)
    away_win_single_game = models.FloatField(null=True)
    away_win_single_set = models.FloatField(null=True)
    away_win_1_set = models.FloatField(null=True)
    away_win_2_set = models.FloatField(null=True)
    home_spw_clay = models.FloatField(null=True)
    home_rpw_clay = models.FloatField(null=True)
    home_dr_clay = models.FloatField(null=True)
    home_matches_clay = models.TextField(null=True)
    away_spw_clay = models.FloatField(null=True)
    away_rpw_clay = models.FloatField(null=True)
    away_dr_clay = models.FloatField(null=True)
    away_matches_clay = models.TextField(null=True)
    stats_win_clay = models.FloatField(null=True)
    home_spw_grass = models.FloatField(null=True)
    home_rpw_grass = models.FloatField(null=True)
    home_dr_grass = models.FloatField(null=True)
    home_matches_grass = models.TextField(null=True)
    away_spw_grass = models.FloatField(null=True)
    away_rpw_grass = models.FloatField(null=True)
    away_dr_grass = models.FloatField(null=True)
    away_matches_grass = models.TextField(null=True)
    stats_win_grass = models.FloatField(null=True)

