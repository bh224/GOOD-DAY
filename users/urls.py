from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from users.apis.v1 import user_api

urlpatterns = [
    path("", views.Users.as_view(), name="user_view"),
    path("me", user_api.UserDetail.as_view()),
    path("check_username", views.CheckUsername.as_view()),
    path("workgroups", views.WorkGroupList.as_view()),
    path("workgroups/<int:pk>", views.WorkGroupDetail.as_view()),
    path("login", views.LogIn.as_view()),
    path("logout", views.LogOut.as_view()),
    path("kakao", views.KakaoLogin.as_view()),
    path("google", views.GoogleLogin.as_view()),
    path("naver", views.NaverLogin.as_view()),
    path("todays", views.Todays.as_view()),
    path("today", views.TodayDetail.as_view()),
    path("token-login", obtain_auth_token),
]
