from django.db import models


# Create your models here.
class Combination(models.Model):
    combination = models.TextField()
    prob = models.FloatField()
    bet = models.BooleanField(default=False)
    list_index = models.IntegerField(default=0)
    vakio_id = models.IntegerField(default=0)
    value = models.IntegerField(null=True, default=None)

    # Composite primary key
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['list_index', 'combination', 'vakio_id'],
                name='unique_combination_id'
            )
        ]


class WinShare(models.Model):
    combination = models.TextField()
    bets = models.IntegerField()
    value = models.IntegerField()
    list_index = models.IntegerField()
    vakio_id = models.IntegerField()

    # Composite primary key
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['list_index', 'combination', 'vakio_id'],
                name='unique_winshare_id'
            )
        ]


class MonivetoProb(models.Model):
    combination = models.TextField()
    prob = models.FloatField()
    score = models.TextField()
    match_nro = models.IntegerField()
    moniveto_id = models.IntegerField()
    list_index = models.IntegerField()

    # Composite primary key
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['list_index', 'combination', 'moniveto_id'],
                name='unique_moniveto_winshare_id'
            )
        ]


class MonivetoOdds(models.Model):
    combination = models.TextField()
    match1 = models.TextField(default="")
    match2 = models.TextField(default="")
    match3 = models.TextField(default="")
    match4 = models.TextField(default="")
    value = models.IntegerField()
    bet = models.BooleanField(default=False)
    list_index = models.IntegerField()
    moniveto_id = models.IntegerField()

    # Composite primary key
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['list_index', 'combination', 'moniveto_id'],
                name='unique_moniveto_odds_id'
            )
        ]


class MonivetoBet(models.Model):
    combination = models.TextField()
    list_index = models.IntegerField()
    value = models.IntegerField(null=True, default=None)
    moniveto_id = models.IntegerField()
    bet = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
