from datetime import datetime, date
from django.db import IntegrityError
from django.db.models import Q
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from tasks.models import Task, Comment
from tasks.services.task_service import get_date_list, get_my_group_task_list, get_my_today_todo_list, get_total_page
from users.models import User, Workgroup


class TestTaskServices(APITestCase):
    def test_create_a_task_without_limit_date(self) -> None:
        # Given
        user = User.objects.create(
            username="test", password="1234", nickname="test_name"
        )
        group = Workgroup.objects.create(group_code="a999", member=user)

        # Expect
        with self.assertRaises(IntegrityError):
            Task.objects.create(
                author=user, content="content", type="task", status="yet", group=group
            )

    # 일정 등록했던 날짜들 리스트 불러오기
    def test_get_dates_list_user_saved(self) -> None:
        # Given
        offset = 0
        limit = 5
        user = User.objects.create(
            username="test", password="1234", nickname="test_name"
        )
        tasks = [
            Task.objects.create(
                author=user,
                content="content",
                type="todo",
                status="doing",
                limit_date="2023-01-31",
            )
            for i in range(10, 21)
        ]

        # When
        result_list = get_date_list(user.pk, offset, limit)

        # Then
        self.assertEqual(1, len(result_list))

    def test_get_total_page(self) -> None:
        # Given
        offset = 10
        user = User.objects.create(
            username="test", password="1234", nickname="test_name"
        )
        user2 = User.objects.create(
            username="test2", password="1234", nickname="test_name"
        )
        todos = [
            Task.objects.create(
                author=user,
                content="todo",
                type="todo",
                status="doing",
                limit_date="2023-12-31",
            )
            for i in range(1, 11)
        ]
        tasks = [
            Task.objects.create(
                author=user2,
                tasker=user,
                content="task",
                type="task",
                status="yet",
                limit_date="2023-12-31",
            )
            for i in range(1, 11)
        ]

        # When
        my_tasks = Task.objects.filter(Q(author_id=user.pk) | Q(tasker=user.pk))

        with CaptureQueriesContext(connection) as ctx:
            total_page = get_total_page(user.pk, offset)

        # Then
        self.assertEqual(20, len(my_tasks))
        self.assertEqual(1, len(total_page))

    def test_get_group_task_list(self) -> None:
        # Given
        user1 = User.objects.create(username="test_user", password="1234", nickname="test_user")
        user2 = User.objects.create(username="test_member", password="1234", nickname="test_member")
        task1 =  Task.objects.create(author=user1, tasker=user2, content="task to you", type="task", status="yet", limit_date="2023-12-31")
        task2 =  Task.objects.create(author=user2, tasker=user1, content="task to me", type="task", status="yet", limit_date="2023-12-31")
        Comment.objects.create(author=user2, task=task2, content="test_comment")

        # When
        with self.assertNumQueries(2):
            tasks = get_my_group_task_list(user1.pk) # 쿼리 1번
            result_comment = [ task.comments.count() for task in tasks ] # tasks 개수만큼 쿼리

        # Then
        self.assertEqual(2, len(tasks))
        self.assertEqual("task", tasks[0].type)
        self.assertEqual(1, result_comment[0])

    def test_get_my_today_todo_list(self) -> None:
        # Given
        user = User.objects.create(username="test_user", password="1234", nickname="test_user")
        [Task.objects.create(author=user, content=f"todo{i}", type="todo", status="doing", limit_date="2023-12-31") for i in range(1, 11)]

        # When
        todo_list = get_my_today_todo_list(user.pk)

        # Then
        self.assertEqual(10, len(todo_list))
        self.assertEqual("todo10", todo_list[0].content)


