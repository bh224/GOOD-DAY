from django.db import models

# Create your models here.
class CommonMode(models.Model):
    """
    created, updated date
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True