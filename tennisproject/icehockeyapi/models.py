from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Teams(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField(null=True)
    name_short = models.TextField(null=True)


class Liiga(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_matches",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_matches",
    )
    challenge_id = models.IntegerField(null=True)
    status = models.TextField(null=True)
    status_more = models.TextField(null=True)
    start_at = models.TextField(null=True, blank=True)
    home_team_name = models.TextField(null=True)
    away_team_name = models.TextField(null=True)
    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)
    winner_code = models.IntegerField(null=True, blank=True)
    home_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    draw_odds = models.FloatField(null=True)
    start_at = models.DateTimeField(null=True, blank=True)

    @property
    def combined_score(self):
        return f'{self.home_score}-{self.away_score}'


class Mestis(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_matches_mestis",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_matches_mestis",
    )
    challenge_id = models.IntegerField(null=True)
    status = models.TextField(null=True)
    status_more = models.TextField(null=True)
    start_at = models.TextField(null=True, blank=True)
    home_team_name = models.TextField(null=True)
    away_team_name = models.TextField(null=True)
    home_score = models.IntegerField(null=True)
    away_score = models.IntegerField(null=True)
    winner_code = models.IntegerField(null=True, blank=True)
    home_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    draw_odds = models.FloatField(null=True)
    start_at = models.DateTimeField(null=True, blank=True)

    @property
    def combined_score(self):
        return f'{self.home_score}-{self.away_score}'


class LiigaElo(models.Model):
    match = models.ForeignKey(
        'Liiga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class LiigaEloHome(models.Model):
    match = models.ForeignKey(
        'Liiga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class LiigaEloAway(models.Model):
    match = models.ForeignKey(
        'Liiga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class MestisElo(models.Model):
    match = models.ForeignKey(
        'Mestis',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_mestis",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_mestis",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class MestisEloHome(models.Model):
    match = models.ForeignKey(
        'Mestis',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_mestis_home",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_mestis_home",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class MestisEloAway(models.Model):
    match = models.ForeignKey(
        'Mestis',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_mestis_away",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_mestis_away",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class BetIceHockey(models.Model):
    # This holds the reference to the content type (league table)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # This is the primary key of the related object from the league table
    object_id = models.TextField()
    # This is the actual reference to the league object (from Bundesliga, SerieA, etc.)
    match = GenericForeignKey('content_type', 'object_id')
    home = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="home_bet",
    )
    away = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="away_bet",
    )
    home_name = models.TextField(null=True)
    away_name = models.TextField(null=True)
    home_odds = models.FloatField(null=True)
    draw_odds = models.FloatField(null=True)
    away_odds = models.FloatField(null=True)
    home_elo = models.FloatField(null=True)
    away_elo = models.FloatField(null=True)
    elo_home = models.FloatField(null=True)
    elo_away = models.FloatField(null=True)
    elo_prob = models.FloatField(null=True)
    elo_prob_home = models.FloatField(null=True)
    preview = models.TextField(null=True)
    reasoning = models.TextField(null=True)
    start_at = models.DateTimeField(null=True)
    home_prob = models.FloatField(null=True)
    draw_prob = models.FloatField(null=True)
    away_prob = models.FloatField(null=True)
    home_yield = models.FloatField(null=True)
    draw_yield = models.FloatField(null=True)
    away_yield = models.FloatField(null=True)
    level = models.TextField(null=True)
    home_est_goals = models.FloatField(null=True)
    away_est_goals = models.FloatField(null=True)
    home_poisson = models.FloatField(null=True)
    draw_poisson = models.FloatField(null=True)
    away_poisson = models.FloatField(null=True)
