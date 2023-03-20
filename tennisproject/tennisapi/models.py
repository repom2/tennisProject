from django.db import models


# Create your models here.
class Tournaments(models.Model):
    id = models.IntegerField(primary_key=True)
    section_id = models.IntegerField(null=True)
    section_slug = models.TextField(null=True)
    section_name = models.TextField(null=True)
    priority = models.TextField(null=True)
    name = models.TextField(null=True)
    slug = models.TextField()
    continent = models.TextField(null=True)
    end_date = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    ground_type = models.TextField(null=True)
    number_of_competitors = models.IntegerField(null=True)
    number_of_sets = models.IntegerField(null=True)
    prize_currency = models.TextField(null=True)
    total_prize_money = models.IntegerField(null=True)