import random
import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from tasks import serializers
from users.serializers import (
    SimpleWorkgroupSerializer,
    TestWorkgroupSerializer,
    UserInfoSerializer,
    UserDetailSerializer,
    WorkgroupIncludingMembers,
    WorkgroupSerializer,
    TodayListSerializer,
)
from users.models import User, Workgroup


class Users(APIView):
    # 모든 유저 불러오기
    def get(self, request):
        all_users = User.objects.all()
        serializer = UserInfoSerializer(all_users, many=True)
        return Response(serializer.data)

    # 유저등록
    def post(self, request):
        # print(request.data)
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
                    # 그룹코드 없는 경우 유저만 생성
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


# ID중복검사 
class CheckUsername(APIView):
    def post(self, request):
        username = request.data.get("username")
        is_exist_user = User.objects.filter(username=username).exists()
        if not is_exist_user:
            return Response({"ok": "사용가능한 ID입니다"})
        # 유저가 있을 경우 유저정보 반환
        else:
            try:
                user = User.objects.get(username=username)
            except Exception:
                raise ParseError("유저 찾기 에러 발생")
            serializer = UserInfoSerializer(user)
            return Response(serializer.data)


class UserDetail(APIView):
    """ 유저정보 """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, context={"request":request})
        return Response(serializer.data)

    # 유저정보 수정  & 회원탈퇴 (status=False) - test done
    def put(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            serializer = UserDetailSerializer(updated_user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        

# class WorkGroupList(APIView):
#     """유저가 가입한 그룹 관련"""

#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # # 모든 그룹 불러오기 (?all)
#         # if bool(request.query_params.dict()) == True:
#         #     groups = Workgroup.objects.all()
#         #     serializer = WorkgroupSerializer(groups, many=True, context={"request":request})
#         #     return Response(serializer.data)
#         # # 유저가 속한 그룹 불러오기
#         # user = request.user
#         # groups = user.workgroups.all()
#         # serializer = WorkgroupSerializer(groups, many=True, context={"request":request})
#         # return Response(serializer.data)

#         # 유저가 속한 그룹 전체 불러오기 - 메인페이지 셀렉트, todo 업로드, 수정 모달
#         if request.query_params.get("page") == "all":
#             user = request.user
#             # groups = user.workgroups.all()
#             # serializer = WorkgroupSerializer(groups, many=True, context={"request":request})
#             mygroups = get_my_group_list(1, request.user.pk, 0, 0)
#             serializer = WorkgroupIncludingMembers(mygroups, many=True, context={"request":request})
#             return Response(serializer.data)
        
#         # 유저가 속한 그룹 5개씩 불러오기 - 메인페이지  Mygroup
#         # GET /api/v1/users/workgroups?page={page}
#         try:
#             page = request.query_params.get("page", 1)
#             page = int(page)
#         except ValueError:
#             page = 1
#         page_size = 5
#         start = (page - 1) * page_size
#         end = start + page_size
#         mygroups = get_my_group_list(0, request.user.pk, start, end)
#         serializer = TestWorkgroupSerializer(mygroups, many=True, context={"request":request})
#         return Response(serializer.data)
#         # return Response({"data": get_my_group_list(request.user.pk, start, end)})

#     # 그룹 생성 - test done
#     def post(self, request):
#         user = request.user
#         code = "a"
#         code += str(random.randrange(100, 999))
#         code = create_a_group_code(code)
#         request.data['group_code'] = code
#         serializer = WorkgroupSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 with transaction.atomic():
#                     workgroup = serializer.save(member=user)
#                     user.workgroups.add(workgroup)
#                     serializer = WorkgroupSerializer(workgroup,  context={'request': request})
#                     return Response(serializer.data)
#             except Exception:
#                 raise ParseError('그룹생성실패')
#         else:
#             return Response(serializer.errors)
        
#     #  그룹 탈퇴  - test done
#     def put(self, request):
#         user = request.user
#         group_pk = request.data['pk']
#         try:
#             workgroup = get_a_group(group_pk)
#         except Workgroup.DoesNotExist:
#             raise NotFound
#         try:
#             if workgroup.member == user:
#                 return Response({"msg": "그룹 호스트는 탈퇴할 수 없습니다"})
#             user.workgroups.remove(workgroup)
#             return Response({"msg": "그룹에서 나오셨습니다"})
#         except Exception:
#             raise ParseError("Please Try Again")
        

        
# @api_view(('GET',))
# def page_lists(request):
#     page_size = 5
#     total_page = get_total_group_page(request.user.pk, page_size)
#     return Response({"mygroup":total_page[0], "allgroup":total_page[1]})

# # 모든그룹 불러오기 GET /api/v1/users/workgroups/all
# @api_view(('GET',))
# def get_all_groups(request):
#     try:
#         page = request.query_params.get("page", 1)
#         page = int(page)
#     except ValueError:
#         page = 1
#     page_size = 5
#     start = (page - 1) * page_size
#     end = start + page_size
#     mygroups = get_all_group_list(request.user.pk, start, end)
#     serializer = SimpleWorkgroupSerializer(mygroups, many=True, context={"request":request})
#     return Response(serializer.data)


class LogIn(APIView):
    """ID/PASSWORD 로그인"""

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError("ID/패스워드 입력은 필수입니다")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"detail": "Login Successed!"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail":"ID/패스워드를 확인해 주세요"})


class LogOut(APIView):
    """로그아웃"""

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
                data={
                    "grant_type": "authorization_code",
                    "client_id": "90eb4807776054920da36cf74a9b006e",
                    "redirect_uri": f"{settings.BASE_URL_LOCAL}/simplelogin/kakao",
                    "code": code,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token = token.json().get("access_token")
            user_data = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            user_data = user_data.json()
            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")
            # 가입된 유저인지 확인( email)
            try:
                user = User.objects.get(email=kakao_account["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=profile["nickname"],
                    email=kakao_account["email"],
                    nickname=profile["nickname"],
                    # avatar=profile["profile_image_url"]
                )
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
                    "client_secret": settings.GG_CLIENT_SECRET,
                    "redirect_uri": f"{settings.BASE_URL_LOCAL}/simplelogin/google",
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token = token.json().get("access_token")
            user_data = requests.get(
                f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token}",
                headers={
                    "Authorization": f"Bearer {token}",
                },
            )
            user_data = user_data.json()
            try:
                user = User.objects.get(email=user_data["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=user_data["email"],
                    email=user_data["email"],
                    # avatar=user_data["picture"]
                )
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
            token = requests.post(
                "https://nid.naver.com/oauth2.0/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": "qW_D7ntXsDAXdVlaJf2B",
                    "client_secret": settings.NV_SECRET,
                    "code": code,
                    "state": "H1GRM1ofvYKBwEtxe2bjHyulgdOlTd3u",  # 상태코드는 나중에 변경
                },
            )
            # print(token.json()) #priint(token)으로만 하면 status code만(200) 반환
            token = token.json().get("access_token")
            user_data = requests.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            user_data = user_data.json().get("response")
            try:
                user = User.objects.get(email=user_data["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=user_data["name"],
                    email=user_data["email"],
                    nickname=user_data["nickname"]
                    # profile_img=user_data['profile_image']
                )
                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)