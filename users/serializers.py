from django.db.models import Prefetch
from rest_framework import serializers
from rest_framework.response import Response
from users.models import User, Workgroup, Today


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("pk", "username", "nickname")


# GET /api/v1/users/workgroups/all
class SimpleWorkgroupSerializer(serializers.ModelSerializer):
    is_member = serializers.SerializerMethodField()
    member_cnt = serializers.SerializerMethodField()

    class Meta:
        model = Workgroup
        fields = ("pk", "group_code", "group_name", "is_member", "description", "member_cnt")

    def get_is_member(self, workgroup):
        request = self.context["request"]
        group_members = workgroup.users.all()
        if request:
            user = request.user
            if user in group_members:
                return True
            else:
                return False
        else:
            return False

    def get_member_cnt(self, workgroup):
        return workgroup.users.count()

class WorkgroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    member = UserInfoSerializer(read_only=True)

    class Meta:
        model = Workgroup
        fields = (
            "pk",
            "group_code",
            "group_name",
            "description",
            "member",
            "members",
            "is_member",
        )

    def get_is_member(self, workgroup):
        request = self.context["request"]
        if request:
            user = request.user
            my_groups = user.workgroups.all()
            if workgroup in my_groups:
                return True
            else:
                return False
        else:
            return False

    def get_members(self, workgroup):

        members = workgroup.users.all()
        serializer = UserInfoSerializer(members, many=True)
        return serializer.data


class TestWorkgroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workgroup
        fields = (
            "pk",
            "group_code",
            "group_name",
            "description",
            "member",
        )

#  GET /api/v1/users/workgroups?page=all
class WorkgroupIncludingMembers(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = Workgroup
        fields = (
            "pk",
            "group_name",
            "members",
        )

    def get_members(self, workgroup):
        # serializer = UserInfoSerializer(members, many=True)
        datas = []
        members = workgroup.users.all()
        for member in members:
            data = {
                "pk": member.pk,
                "username": member.username,
                "nickname": member.nickname
            }
            datas.append(data)

        return datas
    
    def get_member(self, workgroup):
        # data = {
        #     "username": workgroup.member.username,
        #     "nickname": workgroup.member.nickname
        # }
        # return data
        return None




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
        fields = (
            "pk",
            "user",
            "start_time",
            "end_time",
            "state_code",
            "created_at",
        )
