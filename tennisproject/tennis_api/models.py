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
    winner_code = models.TextField(null=True)
