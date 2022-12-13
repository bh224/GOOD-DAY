from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from users.serializers import UserInfoSerializer, WorkgroupSerializer
from .models import Task, Comment


class TasksListSerializers(ModelSerializer):
    # author = UserInfoSerializer(read_only=True)
    # tasker = UserInfoSerializer(read_only=True)
    counts = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = (
            "pk",
            "author",
            "tasker",
            "type",
            "content",
            "status",
            "created_at",
            "limit_date",
            "counts"
        )


    def __str__(self):
        return self.name

    def get_counts(self, task):
        return task.comment_count()


class TaskSerializer(ModelSerializer):
    #read-only 이기때문에 request.data 로 받지 않아도 된다
    author = UserInfoSerializer(read_only=True)
    tasker = UserInfoSerializer(read_only=True)
    group = WorkgroupSerializer(read_only=True)
    # limit_date = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Task
        fields = (
            "pk",
            "author",
            "tasker",
            "content",
            "type",
            "limit_date",
            "status",
            "group",
        )

    # def get_limit_date(self, task):
    #     print("===here")
    #     limit_date = task.limit_date
    #     limit_date = limit_date.strftime("%Y-%m-%d")
    #     # limit_date = f"{limit_date.year}-{limit_date.month:%m}-{limit_date.day:%d}"
    #     return limit_date

class CommentSerializer(ModelSerializer):
    task = TasksListSerializers(read_only=True)
    author = UserInfoSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("pk", "author", "content", "task", "created_at")

