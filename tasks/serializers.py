from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from users.serializers import UserInfoSerializer
from .models import Task, Comment


class TasksListSerializers(ModelSerializer):
    # author = UserInfoSerializer(read_only=True)
    # tasker = UserInfoSerializer(read_only=True)

    task_kind = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "pk",
            "author",
            "tasker",
            "type",
            "content",
            "status",
            "task_kind",
            "created_at",
            "limit_date",
        )

    def __str__(self):
        return self.name

    # 내가 다른 유저에게 할당한 task 표시
    def get_task_kind(self, task):
        request = self.context.get("request")
        # 내가 등록한 나의 task
        if task.tasker == None:
            return "myself"
        # 내가 남한테 준 task
        elif (task.author != task.tasker) and (task.author == request.user):
            return "toyou"
        # 남이 나한테 준 task
        return "tome"


class TaskSerializer(ModelSerializer):
    #read-only 이기때문에 request.data 로 받지 않아도 된다
    author = UserInfoSerializer(read_only=True)
    tasker = UserInfoSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = "__all__"

class CommentSerializer(ModelSerializer):
    task = TasksListSerializers(read_only=True)
    author = UserInfoSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = "__all__"