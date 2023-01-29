from datetime import datetime
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from tasks.models import Task, Comment
from tasks.services.task_service import get_task_list
from users.models import User

class TestCommentService(APITestCase):

    # 일정 리스트 가져오기
    def test_get_tasks_attached_comments(self) -> None:
        # Given
        content = "add_comment"
        user = User.objects.create(username="test", password="1234", nickname="test_name")
        task  = Task.objects.create(author=user, content=content, type="todo", status="doing", limit_date="2023-01-01")
        
        # When
        comment = Comment.objects.create(task=task, author=user, content=content)

        # Then
        self.assertEqual(1, len(task.comments.all()))
        self.assertEqual(task.pk, comment.task.pk)

    # 코멘트 개수 구하기
    def test_get_commnet_counts(self) -> None:
    # Given
        user = User.objects.create(username="test", password="1234", nickname="test_name")
        for i in range(1,11):
            task  = Task.objects.create(author=user, content="content", type="todo", status="doing", limit_date="2023-01-01")
            Comment.objects.create(task=task, author=user, content=f"comment{i}")

    #When
        with CaptureQueriesContext(connection) as ctx:
        # with self.assertNumQueries(2):
            result_tasks = get_task_list()
            result_comments = [a.comments.count() for a in result_tasks]
    
    # Then
        self.assertEqual(10, len(result_comments))


