from django.db import models


# Create your models here.
class Tournaments(models.Model):
    id = models.IntegerField(primary_key=True)
    section_id = models.IntegerField(null=True)
    section_slug = models.TextField(null=True)
    section_name = models.TextField(null=True)
    priority = models.TextField(null=True)
    name = models.TextField(null=True)
    slug = models.TextField()
    continent = models.TextField(null=True)
    end_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    ground_type = models.TextField(null=True)
    number_of_competitors = models.IntegerField(null=True)
    number_of_sets = models.IntegerField(null=True)
    prize_currency = models.TextField(null=True)
    total_prize_money = models.IntegerField(null=True)


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


class AtpMatches(models.Model):
    id = models.TextField(primary_key=True)
    tour = models.ForeignKey(
        to=AtpTour,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="atptours",
    )
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
    tour = models.ForeignKey(
        to=WtaTour,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="atptours",
    )
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


class Match(models.Model):
    id = models.TextField(primary_key=True)
    tour = models.ForeignKey(
        to=AtpTour,
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
        related_name="home",
    )
    away = models.ForeignKey(
        to=Players,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="away",
    )
    start_at = models.DateTimeField(null=True)
    round_name = models.TextField(null=True)
    match_num = models.IntegerField(null=True)
    home_odds = models.TextField(null=True)
    away_odds = models.TextField(null=True)


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


class WtaMatch(models.Model):
    id = models.TextField(primary_key=True)
    tour = models.ForeignKey(
        to=WtaTour,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="wtamatches",
    )
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
    start_at = models.DateTimeField(null=True)
    round_name = models.TextField(null=True)
    match_num = models.IntegerField(null=True)
    home_odds = models.TextField(null=True)
    away_odds = models.TextField(null=True)
