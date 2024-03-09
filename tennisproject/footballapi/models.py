from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


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


class FaCup(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_fa_cup_matches",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_fa_cup_matches",
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


class LaLiga(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_laliga_matches",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_laliga_matches",
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

class LaLigaElo(models.Model):
    match = models.ForeignKey(
        'LaLiga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_laliga",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_laliga",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class LaLigaEloHome(models.Model):
    match = models.ForeignKey(
        'LaLiga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home_laliga",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home_laliga",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class LaLigaEloAway(models.Model):
    match = models.ForeignKey(
        'LaLiga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away_laliga",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away_laliga",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class SerieA(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_seriea_matches",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_seriea_matches",
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

class SerieAElo(models.Model):
    match = models.ForeignKey(
        'SerieA',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_seriea",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_seriea",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class SerieAEloHome(models.Model):
    match = models.ForeignKey(
        'SerieA',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home_seriea",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home_seriea",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class SerieAEloAway(models.Model):
    match = models.ForeignKey(
        'SerieA',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away_seriea",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away_seriea",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class Bundesliga(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_bundesliga_matches",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_bundesliga_matches",
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


class AllLeagues(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_all_matches",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_all_matches",
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


class BundesligaElo(models.Model):
    match = models.ForeignKey(
        'Bundesliga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_bundesliga",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_bundesliga",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class BundesligaEloHome(models.Model):
    match = models.ForeignKey(
        'Bundesliga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home_bundesliga",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home_bundesliga",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class BundesligaEloAway(models.Model):
    match = models.ForeignKey(
        'Bundesliga',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away_bundesliga",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away_bundesliga",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class Ligue1(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(null=True)
    name = models.TextField(null=True)
    home_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="home_ligue1_matches",
    )
    away_team = models.ForeignKey(
        Teams,
        on_delete=models.DO_NOTHING,
        related_name="away_ligue1_matches",
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

class Ligue1Elo(models.Model):
    match = models.ForeignKey(
        'Ligue1',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_ligue1",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_ligue1",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class Ligue1EloHome(models.Model):
    match = models.ForeignKey(
        'Ligue1',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home_ligue1",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_home_ligue1",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class Ligue1EloAway(models.Model):
    match = models.ForeignKey(
        'Ligue1',
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away_ligue1",
    )
    team = models.ForeignKey(
        to=Teams,
        on_delete=models.DO_NOTHING,
        related_name="elo_rating_away_ligue1",
    )
    elo = models.IntegerField()
    elo_change = models.IntegerField()
    games = models.IntegerField()
    date = models.DateField(null=True)


class BetFootball(models.Model):
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
