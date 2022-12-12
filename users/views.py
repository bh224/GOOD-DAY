import requests
import random
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User, Workgroup, Today
from .serializers import UserInfoSerializer, UserDetailSerializer, WorkgroupSerializer, TodayListSerializer

# Create your views here.
# 유저랑 같은 그룹 & 그 그룹 멤버 불러오기

class Users(APIView):
    def get(self, request):
        all_users = User.objects.all()
        serializer = UserInfoSerializer(all_users, many=True)
        return Response(serializer.data)

    # 유저등록
    def post(self, request):
        print(request.data)
        password = request.data.get("password")
        if not password:
            raise ParseError("비밀번호는 필수값입니다")
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
                            user = serializer.save()
                            user.set_password(password)
                            user.save()
                            user.workgroups.add(workgroup)
                            # print(workgroup.users.all())
                            serializer = UserDetailSerializer(user)
                            return Response(serializer.data)
                        # 그룹코드 없는 경우(group_code=9999) 유저만 생성
                        else:
                            user = serializer.save()
                            user.set_password(password)
                            user.save()
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
        # print(username)
        is_exist_user = User.objects.filter(username=username).exists()
        if not is_exist_user:
            # print(is_exist_user)
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

    # 새로운 그룹 생성
    def post(self, request):
        user = request.user
        code = str(random.randrange(100, 999))
        request.data['group_code'] += code
        serializer = WorkgroupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    workgroup = serializer.save(member=user)
                    user.workgroups.add(workgroup)
                    serializer = WorkgroupSerializer(workgroup)
                    return Response(serializer.data)
            except Exception:
                raise ParseError("그룹생성실패")
        else:
            return Response(serializer.errors)


class WorkGroupDetail(APIView):
    def get_group(self, pk):
        try:
            return Workgroup.objects.get(pk=pk)
        except Workgroup.DoesNotExist:
            raise NotFound
    def get(self, request, pk):
        workgroup = self.get_group(pk)
        serializer = WorkgroupSerializer(workgroup)
        return Response(serializer.data)
    #그룹에 멤버 추가
    def post(self, request, pk):
        workgroup = self.get_group(pk)
        member_pk = request.data["member_pk"]
        try:
            member = User.objects.get(pk=member_pk)
        except User.DoesNotExist:
            raise NotFound
        member.workgroups.add(workgroup)
        serializer = UserDetailSerializer(member)
        return Response(serializer.data)

    # 그룹명 수정
    def put(self, request, pk):
        workgroup = self.get_group(pk)
        serializer = WorkgroupSerializer(workgroup, data=request.data, partial=True)
        if serializer.is_valid():
            workgroup = serializer.save()
            serializer = WorkgroupSerializer(workgroup)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    # 그룹삭제
    def delete(self, request, pk):
        workgroup = self.get_group(pk)
        if workgroup.member != request.user:
            raise PermissionDenied
        workgroup.delete()
        return Response({"msg":"그룹삭제완료"})

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


# 간편로그인
class KakaoLogin(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")
            # print("code", code)
            token = requests.post(
                "https://kauth.kakao.com/oauth/token",
                data = {
                    "grant_type": "authorization_code",
                    "client_id": "90eb4807776054920da36cf74a9b006e",
                    "redirect_uri": "http://127.0.0.1:3000/simplelogin/kakao",
                    "code": code
                },
                headers= {"Content-Type": "application/x-www-form-urlencoded"},
                )
            token = token.json().get("access_token")
            user_data = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers= {
                    "Authorization": f"Bearer {token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
                }
            )
            # print(user_data.json())
            user_data = user_data.json()
            kakao_account = user_data.get("kakao_account")
            # print(kakao_account)
            profile = kakao_account.get("profile")
            #가입된 유저인지 확인( email)
            try:
                user = User.objects.get(email=kakao_account["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username = profile["nickname"],
                    email=kakao_account["email"],
                    nickname =profile["nickname"],
                    # avatar=profile["profile_image_url"]
                )
                # print(user)
                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:        
            return Response(status=status.HTTP_400_BAD_REQUEST)

class GoogleLogin(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")
            token = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": "1051453023789-boperin529q0af3mf1idkqlplqmt60hs.apps.googleusercontent.com",
                    "client_secret": "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",
                    "redirect_uri": "http://127.0.0.1:3000/simplelogin/google",
                    "grant_type": "authorization_code"
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            token = token.json().get("access_token")
            # print("token", token)
            user_data = requests.get(
                f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token}",
                headers={
                    "Authorization": f"Bearer {token}",
                }
            )
            user_data = user_data.json()
            # print(user_data)
            try:
                user = User.objects.get(email=user_data["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username = user_data["email"],
                    email=user_data["email"],
                    # avatar=user_data["picture"]
                )
                # print(user)
                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class NaverLogin(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")
            # print("code>>>>>>>>>>", code)
            token = requests.post(
                "https://nid.naver.com/oauth2.0/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": "qW_D7ntXsDAXdVlaJf2B",
                    "client_secret": settings.NV_SECRET,
                    "code" : code,
                    "state": "H1GRM1ofvYKBwEtxe2bjHyulgdOlTd3u" #상태코드는 나중에 변경
                }
            )
            # print(token.json()) #priint(token)으로만 하면 status code만(200) 반환
            token = token.json().get("access_token")
            user_data = requests.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )
            user_data = user_data.json().get("response")
            try:
                user = User.objects.get(email=user_data["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=user_data['name'],
                    email=user_data['email'],
                    nickname=user_data['nickname']
                    # profile_img=user_data['profile_image']
                )
                # print(user)
                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:    
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Todays(APIView):
    #쿼리파라미터로 해당날짜 받아오기
    def get(self, request):
        todays = Today.objects.all()
        serializer = TodayListSerializer(todays, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TodayListSerializer(data=request.data)
        if serializer.is_valid():
            today = serializer.save(user=request.user)
            serializer = TodayListSerializer(today)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class TodayDetail(APIView):
    # 쿼리파라미터로 해당날짜 받아오기
    def get_today(self, pk):
        try:
            return Today.objects.get(pk=pk)
        except Today.DoesNotExist:
            raise NotFound
    # 오늘 상황 불러오기
    def get(self, request, pk):
        today = self.get_today(pk)
        serializer = TodayListSerializer(today)
        return Response(serializer.data)

    # 오늘 상황 수정하기
    def put(self, request, pk):
        today = self.get_today(pk)
        serializer = TodayListSerializer(today, data=request.data, partial=True)
        if serializer.is_valid():
            new_today = serializer.save()
            serializer = TodayListSerializer(new_today)
            return Response(serializer.data)
        return Response(serializer.errors)
