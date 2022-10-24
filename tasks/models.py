from email.policy import default
from random import choices
from django.db import models

from common.models import CommonMode

# Create your models here.
class Task(CommonMode):
    class TaskTypeChoices(models.TextChoices):
        TASK = ("task", "task")
        TODO = ("todo", "to-do")
        PRIVATE = ("private", "priv")
        
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE)
    in_charge = models.ForeignKey("users.User", on_delete=models.SET_NULL)
    content = models.CharField(max_length=250)
    type = models.CharField(max_length=20, choices=TaskTypeChoices.choices)
    limit_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=20, default="doing")

