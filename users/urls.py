from django.urls import path
from . import views

urlpatterns = [
    path("", views.Users.as_view()),
    path("me", views.UserDetail.as_view()),
    path("workgroups", views.WorkGroupList.as_view()),
    path("check_username", views.CheckUsername.as_view()),
    path("login", views.LogIn.as_view()),
    path("logout", views.LogOut.as_view()),
]
