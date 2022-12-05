from rest_framework import serializers
from rest_framework.response import Response
from .models import User, Workgroup, Today


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("pk", "username", "nickname")


class WorkgroupSerializer(serializers.ModelSerializer):
    # member = UserInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Workgroup
        fields = ("pk", "group_code", "group_name")


class UserDetailSerializer(serializers.ModelSerializer):
    workgroups = WorkgroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "pk",
            "username",
            "nickname",
            "email",
            "status",
            "workgroups",
        )
