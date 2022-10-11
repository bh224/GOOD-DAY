from django.db import models

# Create your models here.
class CommonMode(models.Model):
    """
    created, updated date
    """

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        abstract = True