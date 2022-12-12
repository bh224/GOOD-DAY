from rest_framework import serializers
from rest_framework.response import Response
from .models import User, Workgroup, Today


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("pk", "username", "nickname")


class WorkgroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Workgroup
        fields = ("pk", "group_code", "group_name", "members")

    def get_members(self, workgroup):
        members = workgroup.users.all()
        # print(members)
        serializer = UserInfoSerializer(members, many=True)
        return serializer.data


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

class TodayListSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)
    class Meta:
        model = Today
        fields = ("pk", "user", "start_time", "end_time", "state_code")