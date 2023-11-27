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
