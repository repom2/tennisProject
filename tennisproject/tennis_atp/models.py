from django.db import models


# Create your models here.
class Players(models.Model):
    player_id = models.TextField(primary_key=True)
    name_first = models.TextField(null=True)
    name_last = models.TextField(null=True)
    hand = models.TextField(null=True)
    dob = models.TextField(null=True)
    ioc = models.TextField(null=True)
    height = models.TextField(null=True)
    wikidata_id = models.TextField(null=True)
