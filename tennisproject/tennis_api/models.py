from django.db import models


class Player(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    residence = models.TextField(null=True)
    birthplace = models.TextField(null=True)
    name_short = models.TextField(null=True)
    name_full = models.TextField(null=True)
    gender = models.TextField(null=True)
    dob = models.DateField(null=True)
    hand = models.TextField(null=True)
    weight = models.TextField(null=True)
    height = models.FloatField(null=True)
    country_code = models.TextField(null=True)
    country = models.TextField(null=True)
    prize_total_euros = models.IntegerField(null=True)
    prize_current_euros = models.IntegerField(null=True)


class AtpTour(models.Model):
    id = models.IntegerField(primary_key=True)
    section_id = models.IntegerField()
    slug = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    city = models.TextField(null=True)
    country = models.TextField(null=True)
    tennis_points = models.IntegerField(null=True)
    number_of_sets = models.IntegerField(null=True)
    surface = models.TextField(null=True)
    currency = models.TextField(null=True)
    prize_money = models.IntegerField(null=True)
    continent = models.TextField(null=True)
    number_of_competitors = models.IntegerField(null=True)
    most_count = models.IntegerField(null=True)


class WtaTour(models.Model):
    id = models.IntegerField(primary_key=True)
    section_id = models.IntegerField()
    slug = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    city = models.TextField(null=True)
    country = models.TextField(null=True)
    tennis_points = models.IntegerField(null=True)
    number_of_sets = models.IntegerField(null=True)
    surface = models.TextField(null=True)
    currency = models.TextField(null=True)
    prize_money = models.IntegerField(null=True)
    continent = models.TextField(null=True)
    number_of_competitors = models.IntegerField(null=True)
    most_count = models.IntegerField(null=True)


class AtpMatch(models.Model):
    id = models.IntegerField(primary_key=True)
    tour = models.ForeignKey(
        to=AtpTour,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="atp_match",
    )
    home = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="home",
    )
    away = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="away",
    )
    start_at = models.DateTimeField(null=True)
    round_name = models.TextField(null=True)
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
    winner_code = models.IntegerField(null=True)
    status = models.TextField(null=True)
    status_more = models.TextField(null=True)
    challenge_id = models.IntegerField(null=True)
    home_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)


class WtaMatch(models.Model):
    id = models.TextField(primary_key=True)
    tour = models.ForeignKey(
        to=WtaTour,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="wta_match",
    )
    home = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="wta_home",
    )
    away = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="wta_away",
    )
    start_at = models.DateTimeField(null=True)
    round_name = models.TextField(null=True)
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
    winner_code = models.IntegerField(null=True)
    status = models.TextField(null=True)
    status_more = models.TextField(null=True)
    challenge_id = models.IntegerField(null=True)
    home_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)


class AtpEloClay(models.Model):
    match = models.ForeignKey(
        'AtpMatch',
        on_delete=models.DO_NOTHING,
        related_name="elo_clay",
    )
    player = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        related_name="elo_clay",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class AtpEloHard(models.Model):
    match = models.ForeignKey(
        'AtpMatch',
        on_delete=models.DO_NOTHING,
        related_name="elo_hard",
    )
    player = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        related_name="elo_hard",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class AtpEloGrass(models.Model):
    match = models.ForeignKey(
        'AtpMatch',
        on_delete=models.DO_NOTHING,
        related_name="elo_grass",
    )
    player = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        related_name="elo_grass",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class BetAtp(models.Model):
    match = models.OneToOneField(
        AtpMatch, on_delete=models.CASCADE
    )
    home = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="bet_home",
    )
    away = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="bet_away",
    )
    home_name = models.TextField(null=True)
    away_name = models.TextField(null=True)
    home_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    elo_prob = models.FloatField(null=True)
    year_elo_prob = models.FloatField(null=True)
    home_spw = models.FloatField(null=True)
    home_rpw = models.FloatField(null=True)
    away_spw = models.FloatField(null=True)
    away_rpw = models.FloatField(null=True)
    home_stat_matches = models.IntegerField(null=True)
    away_stat_matches = models.IntegerField(null=True)
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


class WtaEloClay(models.Model):
    match = models.ForeignKey(
        'WtaMatch',
        on_delete=models.DO_NOTHING,
        related_name="wta_elo_clay",
    )
    player = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        related_name="wta_elo_clay",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class WtaEloHard(models.Model):
    match = models.ForeignKey(
        'WtaMatch',
        on_delete=models.DO_NOTHING,
        related_name="wta_elo_hard",
    )
    player = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        related_name="wta_elo_hard",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class WtaEloGrass(models.Model):
    match = models.ForeignKey(
        'WtaMatch',
        on_delete=models.DO_NOTHING,
        related_name="wta_elo_grass",
    )
    player = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        related_name="wta_elo_grass",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class BetWta(models.Model):
    match = models.OneToOneField(
        WtaMatch, on_delete=models.CASCADE
    )
    home = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="bet_wta_home",
    )
    away = models.ForeignKey(
        to=Player,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="bet_wta_away",
    )
    home_name = models.TextField(null=True)
    away_name = models.TextField(null=True)
    home_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    elo_prob = models.FloatField(null=True)
    year_elo_prob = models.FloatField(null=True)
    home_spw = models.FloatField(null=True)
    home_rpw = models.FloatField(null=True)
    away_spw = models.FloatField(null=True)
    away_rpw = models.FloatField(null=True)
    home_stat_matches = models.IntegerField(null=True)
    away_stat_matches = models.IntegerField(null=True)
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
