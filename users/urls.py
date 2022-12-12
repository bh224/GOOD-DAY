from django.urls import path
from . import views

urlpatterns = [
    path("", views.Users.as_view()),
    path("me", views.UserDetail.as_view()),
    path("workgroups", views.WorkGroupList.as_view()),
    path("workgroups/<int:pk>", views.WorkGroupDetail.as_view()),
    path("check_username", views.CheckUsername.as_view()),
    path("todays", views.Todays.as_view()),
    path("todays/<int:pk>", views.TodayDetail.as_view()),
    path("login", views.LogIn.as_view()),
    path("logout", views.LogOut.as_view()),
    path("kakao", views.KakaoLogin.as_view()),
    path("google", views.GoogleLogin.as_view()),
    path("naver", views.NaverLogin.as_view()),
]
