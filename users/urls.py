from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from users.apis.v1 import user_api, group_api

urlpatterns = [
    path("", user_api.Users.as_view(), name="user_view"),
    path("me", user_api.UserDetail.as_view()),
    path("check-username", user_api.CheckUsername.as_view()),
    path("login", user_api.LogIn.as_view()),
    path("logout", user_api.LogOut.as_view()),
    path("kakao", user_api.KakaoLogin.as_view()),
    path("google", user_api.GoogleLogin.as_view()),
    path("naver", user_api.NaverLogin.as_view()),
    path("workgroups", group_api.WorkGroupList.as_view()),
    path("workgroups/<int:pk>", group_api.WorkGroupDetail.as_view()),
    path("workgroups/all", group_api.get_all_groups),
    path("workgroups/pages", group_api.page_lists),
    path("workgroups/check-username", group_api.check_username_in_group),
    path("todays", views.Todays.as_view()),
    path("today", views.TodayDetail.as_view()),
    path("token-login", obtain_auth_token),
]
