from random import choices
from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models import CommonMode

# Create your models here.
class User(AbstractUser):
    group_name = models.CharField(max_length=120, null=True, blank=True)
    nickname = models.CharField(max_length=50, default="")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Today(CommonMode):
    class TodayStateChoices(models.TextChoices):
        ON = "on", "On"
        OFF = "off", "Off"
        BREAK = "break", "Break Time"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    state_code =  models.CharField(max_length=20, choices=TodayStateChoices.choices)
