from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User, Workgroup
from .serializers import UserInfoSerializer, UserDetailSerializer, WorkgroupSerializer

# Create your views here.
# 유저랑 같은 그룹 & 그 그룹 멤버 불러오기


class Users(APIView):
    def get(self, request):
        all_users = User.objects.all()
        serializer = UserInfoSerializer(all_users, many=True)
        return Response(serializer.data)

    # 유저등록
    def post(self, request):
        password = request.data.get("password")
        group_code = request.data.get("group_code")
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # 그룹추가
                    if group_code:
                        # 그룹코드 존재하는 경우
                        if Workgroup.objects.filter(group_code=group_code).exists():
                            workgroup = Workgroup.objects.get(group_code=group_code)
                            # user = serializer.save(worksgroups=workgroup)
                            user = serializer.save()
                            user.set_password(password)
                            user.workgroups.add(workgroup)
                            # print(workgroup.users.all())
                            serializer = UserDetailSerializer(user)
                            return Response(serializer.data)
                        # 그룹코드 없는 경우 유저만 생성
                        else:
                            user = serializer.save()
                            user.set_password(password)
                            serializer = UserDetailSerializer(user)
                            return Response(serializer.data)
            except Exception:
                raise ParseError("transaction error")
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

# ID중복검사
class CheckUsername(APIView):
    def post(self, request):
        username = request.data.get("username")
        print(username)
        is_exist_user = User.objects.filter(username=username).exists()
        if is_exist_user:
            print(is_exist_user)
            return Response({"ok":"사용가능한 ID입니다"})
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

# 유저가 속한 그룹
class WorkGroupList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        groups = user.workgroups.all()
        serializer = WorkgroupSerializer(groups, many=True)
        return Response(serializer.data)


class LogIn(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError("ID/패스워드 입력은 필수입니다")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"ok": "Login Successed!"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="ID/패스워드를 확인해 주세요")


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": "Logout Successed!"})
