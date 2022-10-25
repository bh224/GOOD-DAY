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

    author = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="chargetask"
    )
    sender = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="sendtask"
    )
    content = models.CharField(max_length=250)
    type = models.CharField(max_length=20, choices=TaskTypeChoices.choices)
    limit_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=20, default="doing")

    def __str__(self):
        return f"Task num: {self.pk}"
