from django.db.models import QuerySet

from tasks.models import Comment

def get_comments_belongs_to_a_task(task_pk: int) -> QuerySet:
    all_comments = Comment.objects.filter(task=task_pk).select_related("author").select_related("task")
    return all_comments