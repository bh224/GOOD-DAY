from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models import CommonMode


# Create your models here.
class User(AbstractUser):
    nickname = models.CharField(max_length=50, default="")
    status = models.BooleanField(default=True)
    workgroups = models.ManyToManyField("users.Workgroup", null=True, blank=True, related_name="users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.username


class Workgroup(CommonMode):
    group_code = models.CharField(max_length=100)
    group_name = models.CharField(max_length=150, null=True, blank=True)
    member = models.ForeignKey("users.User", on_delete=models.CASCADE)  #그룹 만든 사람

    def __str__(self):
        return self.group_name



class Today(CommonMode):
    class TodayStateChoices(models.TextChoices):
        ON = "on", "On"
        OFF = "off", "Off"
        BREAK = "break", "Break Time"

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    state_code =  models.CharField(max_length=20, choices=TodayStateChoices.choices)    