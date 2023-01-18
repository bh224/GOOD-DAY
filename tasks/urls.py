from django.urls import path
from . import views

urlpatterns = [
    path("", views.Tasks.as_view()),
    path("tome/", views.TasksToMe.as_view()),
    path("all/", views.AllTasks.as_view()),
    path("<int:pk>/", views.TaskDetail.as_view()),
    path("group/<int:pk>", views.GroupTasks.as_view()),
    path("<int:pk>/comments/", views.Comments.as_view()),
    path("<int:pk>/comments/<int:comment_id>", views.CommentDetail.as_view()),
    path("tasks-counts", views.task_counts),
]
