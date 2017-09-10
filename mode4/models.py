from django.db import models

class NamedGraph(models.Model):
    description = models.TextField()
    pickled_graph = models.TextField()

