from django.db import models


class Player(models.Model):
    id = models.TextField(primary_key=True)
    dob = models.DateField(null=True)
    hand = models.TextField(null=True)
    country_code = models.TextField(null=True)
    height = models.FloatField(null=True)
    first_name = models.TextField(null=True)
    last_name = models.TextField(null=True)
    slug = models.TextField(null=True)
    country = models.TextField(null=True)
    prize_total_euros = models.IntegerField(null=True)


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
