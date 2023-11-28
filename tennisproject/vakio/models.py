from django.db import models


# Create your models here.
class Combination(models.Model):
    id = models.TextField(primary_key=True)
    prob = models.FloatField()
    bet = models.BooleanField(default=False)


class WinShare(models.Model):
    id = models.TextField(primary_key=True)
    bets = models.IntegerField()
    value = models.IntegerField()


class MonivetoProb(models.Model):
    id = models.TextField(primary_key=True)
    prob = models.FloatField()
    score = models.TextField()
    match_nro = models.IntegerField()


class MonivetoOdds(models.Model):
    id = models.TextField(primary_key=True)
    match1 = models.TextField(default="")
    match2 = models.TextField(default="")
    match3 = models.TextField(default="")
    match4 = models.TextField(default="")
    value = models.IntegerField()
