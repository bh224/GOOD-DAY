from django.db import models

from common.models import CommonMode

# Create your models here.
class Comment(CommonMode):
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE)
    author = models.ForeignKey("users.User", on_delete=models.CASCADE)
    content = models.TextField()
    