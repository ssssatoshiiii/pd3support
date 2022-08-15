from django.db import models

class Graph(models.Model):
    title = models.CharField(max_length=255)
    uri = models.CharField(max_length=255)

# Create your models here.
