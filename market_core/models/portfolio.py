from django.db import models

class Portfolio(models.Model):
    name = models.CharField(max_length=300, null=False)
    description = models.TextField(null=True, blank=True)
