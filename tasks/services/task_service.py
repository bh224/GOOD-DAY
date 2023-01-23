import math
from datetime import datetime, date
from typing import List, Tuple
from django.db.models import QuerySet, Q, Count
from tasks.models import Task


def get_task_list() -> QuerySet:
    return Task.objects.all().prefetch_related("comments")
    # return Task.objects.all()


# task에 달린 comment 개수 -> Task 모델에 칼럼추가
# def get_comment_counts_attached_a_task(pk: int) -> int:
#     return Task.objects.filter(pk=pk).prefetch_related("comments").count()

# 오늘의 그룹일정
def get_my_group_task_list(user_pk: int) -> QuerySet:
    today = datetime.now()
    my_group_tasks = Task.objects.filter(
        Q(author=user_pk) | Q(tasker=user_pk),
        created_at__date=date(today.year, today.month, today.day),
        type="task",
    ).prefetch_related("comments").order_by("-created_at")
    return my_group_tasks

# 오늘의 일정
def get_my_today_todo_list(user_pk: int) -> QuerySet:
    today = datetime.now()
    my_todo_list = Task.objects.filter(
        ~Q(type="task"),
        author=user_pk,
        created_at__date=date(today.year, today.month, today.day)
    ).prefetch_related("comments").order_by("-created_at")
    return my_todo_list


def get_date_list(user_id: int, offset: int, limit: int) -> List[str]:
    date_list = []
    all_tasks = (
        Task.objects.filter(Q(author_id=user_id) | Q(tasker=user_id))
        .values("created_at__date")
        .annotate(count=Count("pk"))
        .order_by("-created_at__date")
    )
    for task in all_tasks[offset:limit]:
        date_list.append(task["created_at__date"].strftime("%Y-%m-%d"))
    return date_list


def get_total_page(user_pk: int, offset: int) -> int:
    total_page = math.ceil(
        Task.objects.filter(Q(author_id=user_pk) | Q(tasker=user_pk)).values("created_at__date").annotate(count=Count("pk")).count() / offset
    )
    return [i for i in range(1, total_page + 1)]
