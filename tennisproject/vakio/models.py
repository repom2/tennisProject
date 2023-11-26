from django.db import models


# Create your models here.
class Combination(models.Model):
    id = models.TextField(primary_key=True)
    prob = models.FloatField()

class Match(models.Model):
    id = models.TextField(primary_key=True)
    value = models.IntegerField()
