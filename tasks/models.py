from django.db import models
from common.models import CommonMode

# Create your models here.
class Task(CommonMode):
    """
    author: 일정 등록한 사람 (일정부여한 사람)
    tasker: 일정을 수행하는 사람, tasker=null -> 자기일정을 자기가 등록
    """

    class TaskTypeChoices(models.TextChoices):
        TASK = ("task", "task")
        TODO = ("todo", "to-do")
        PRIVATE = ("private", "priv")

    author = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="chargetask"
    )
    tasker = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sendtask",
    )
    group = models.ForeignKey("users.Workgroup", on_delete=models.CASCADE, null=True, blank=True)
    content = models.CharField(max_length=250)
    type = models.CharField(max_length=20, choices=TaskTypeChoices.choices)
    limit_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default="doing")

    def __str__(self):
        return f"Task num: {self.pk}"
        
    # 코멘트 개수
    def comment_count(self):
        return self.comments.count()

class Comment(CommonMode):
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()

    def __str__(self):
        return f"{self.task.pk} : {self.content}"


