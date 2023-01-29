from dataclasses import fields
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from users.serializers import (
    SimpleWorkgroupSerializer,
    UserInfoSerializer,
    WorkgroupSerializer,
)
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
            "counts",
        )

    def __str__(self):
        return self.name

    def get_counts(self, task):
        return task.comments.count()
        # return task.comment_cnt


class TaskSerializer(ModelSerializer):
    # read-only 이기때문에 request.data 로 받지 않아도 된다
    # author = UserInfoSerializer(read_only=True)
    # tasker = UserInfoSerializer(read_only=True)
    # group = SimpleWorkgroupSerializer(read_only=True)

    author = serializers.SerializerMethodField("get_author_info")
    tasker = serializers.SerializerMethodField("get_tasker_info")
    group = serializers.SerializerMethodField("get_group_info")

    def get_author_info(self, task):
        data = {
            "pk": task.author.pk,
            "username": task.author.username,
            "nickname": task.author.nickname,
        }
        return data

    def get_tasker_info(self, task):
        try:
            data = {
                "pk": task.tasker.pk,
                "username": task.tasker.username,
                "nickname": task.tasker.nickname,
            }
            return data
        except AttributeError:
            return None

    def get_group_info(self, task):
        try:
            data = {
                "pk": task.group.pk,
                "group_code": task.group.group_code,
                "group_name": task.group.group_name,
                "description": task.group.description,

            }
            return data
        except AttributeError:
            return None

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


class CommentSerializer(ModelSerializer):
    # task = TasksListSerializers(read_only=True)
    # author = UserInfoSerializer(read_only=True)
    author = serializers.SerializerMethodField("get_comments_author")

    def get_comments_author(self, comment):
        data = {
            "pk": comment.author.pk,
            "username": comment.author.username,
            "nickname": comment.author.nickname
        }
        return data

    class Meta:
        model = Comment
        fields = ("pk", "author", "content", "created_at")


class CreateCommentSerializer(ModelSerializer):
    task = TasksListSerializers(read_only=True)
    author = UserInfoSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("pk", "author", "content", "task", "created_at")


class CreateTaskSerializer(ModelSerializer):
    author = UserInfoSerializer(read_only=True)
    tasker = UserInfoSerializer(read_only=True)
    group = SimpleWorkgroupSerializer(read_only=True)

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