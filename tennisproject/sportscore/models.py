from django.db import models


# Create your models here.
class Leagues(models.Model):
    id = models.TextField(primary_key=True)
    sport_id = models.TextField()
    section_id = models.TextField()
    slug = models.TextField(null=True)
    name_translations = models.JSONField(null=True)
    has_logo = models.BooleanField(null=True)
    logo = models.TextField(null=True)
    start_date = models.TextField(null=True, blank=True)
    end_date = models.TextField(null=True, blank=True)
    priority = models.TextField(null=True)
    host = models.JSONField(null=True)
    tennis_points = models.TextField(null=True)
    facts = models.JSONField(null=True)
    most_count = models.TextField(null=True)
    section = models.JSONField(null=True)
    sport = models.JSONField(null=True)

