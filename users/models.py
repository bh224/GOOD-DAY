from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models import CommonMode

# Create your models here.
class User(AbstractUser):
    group_code = models.CharField(max_length=120)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    team = models.CharField(max_length=20, null=True)
    position = models.CharField(max_length=20, null=True)
    hr_permit = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    work_start = models.DateField()
    work_end = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TodayState(CommonMode):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    state_code =  models.PositiveIntegerField()
