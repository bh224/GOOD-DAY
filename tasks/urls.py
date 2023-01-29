from django.urls import path

from tasks.apis.v1 import task_api, comment_api
from . import views

urlpatterns = [
    path("", task_api.Tasks.as_view()), #오늘 일정
    path("my-group/", task_api.MyGroupTasks.as_view()), #오늘 그룹일정
    path("daily-task", task_api.daily_tasks_list), #특정날짜에 등록한 일정
    path("date-list/", task_api.date_list),
    path("pages/", task_api.page_list),
    path("<int:pk>/", task_api.TaskDetail.as_view()),
    path("group/<int:pk>", task_api.GroupTasks.as_view()), #그룹 멤버들의 일정
    path("progress", task_api.task_counts),
    path("<int:pk>/comments/", comment_api.Comments.as_view()),
    path("<int:pk>/comments/<int:comment_id>", comment_api.CommentDetail.as_view()),
]
