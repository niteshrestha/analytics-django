from django.db import models


class Visit(models.Model):
    year = models.IntegerField(default=2020)
    month = models.IntegerField(default=0)
    day = models.IntegerField(default=0)
    domain = models.CharField(max_length=255)
    details = models.TextField()
