from django.db import models

#by default null=False, blank=False
class NamedGraph(models.Model):
    description = models.TextField()
    pickled_graph = models.TextField()