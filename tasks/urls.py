from django.urls import path

from tasks.apis.v1 import task_api
from . import views

urlpatterns = [
    path("", task_api.Tasks.as_view()),
    path("my-group/", task_api.MyGroupTasks.as_view()),
    # path("tome/", views.TasksToMe.as_view()),
    # path("all/", views.AllTasks.as_view()),
    path("all/", task_api.date_list),
    path("daily-task", task_api.daily_tasks_list),
    path("<int:pk>/", views.TaskDetail.as_view()),
    path("group/<int:pk>", views.GroupTasks.as_view()),
    path("<int:pk>/comments/", views.Comments.as_view()),
    path("<int:pk>/comments/<int:comment_id>", views.CommentDetail.as_view()),
    path("tasks-counts", views.task_counts),
]
