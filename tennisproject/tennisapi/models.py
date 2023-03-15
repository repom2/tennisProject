from django.db import models


# Create your models here.
class Tournaments(models.Model):
    id = models.IntegerField(primary_key=True)
    slug = models.TextField()