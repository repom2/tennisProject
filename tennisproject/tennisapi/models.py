from django.db import models


# Create your models here.
class Tournaments(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.TextField()
    continent = models.TextField(null=True)
    end_date = models.DateTimeField(null=True)
    start_date_date = models.DateTimeField(null=True)
    ground_type = models.TextField(null=True)
    number_of_competitors = models.IntegerField(null=True)
    number_of_sets = models.IntegerField(null=True)
    prize_currency = models.TextField(null=True)
    total_prize_money = models.IntegerField(null=True)