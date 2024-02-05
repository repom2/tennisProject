from django.db import models


class Teams(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField(null=True)
    name_short = models.TextField(null=True)

class PremierLeague(models.Model):
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


class Championship(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_championship_matches",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_championship_matches",
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
    start_at = models.DateTimeField(null=True, blank=True, default=None)


class PremierElo(models.Model):
    match = models.ForeignKey(
        'PremierLeague',
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


class PremierEloHome(models.Model):
    match = models.ForeignKey(
        'PremierLeague',
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


class PremierEloAway(models.Model):
    match = models.ForeignKey(
        'PremierLeague',
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


class ChampionshipElo(models.Model):
    match = models.ForeignKey(
        'Championship',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="championship_elo_rating",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class ChampionshipEloHome(models.Model):
    match = models.ForeignKey(
        'Championship',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="championship_home_elo_rating",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class ChampionshipEloAway(models.Model):
    match = models.ForeignKey(
        'Championship',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="championship_away_elo_rating",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)
