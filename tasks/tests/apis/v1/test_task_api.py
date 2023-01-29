from datetime import date, datetime
from rest_framework.test import APITestCase

from users.models import User
from tasks.models import Task, Comment

class TestTasksAPI(APITestCase):

    def user_logged_in(self):
        user = User.objects.create(username="test_user")
        user.set_password("1234")
        user.save()
        self.user = user
        self.client.force_login(self.user)
        return user

    def test_date_list(self) -> None:
        # Given
        user = self.user_logged_in()
        [
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
        response = self.client.get(
            "/api/v1/tasks/all/",  {"page": 1},
        )

        data = response.json()

        # Then
        self.assertEqual(1, len(data['data']))
        self.assertEqual(date.today().isoformat(), data["data"][0])

    def test_get_my_group_task_today(self) -> None:
        # Given
        user1 = self.user_logged_in()
        user2 = User.objects.create(username="test_member", password="1234", nickname="test_member")
        task1 =  Task.objects.create(author=user1, tasker=user2, content="task to you", type="task", status="yet", limit_date="2023-12-31")
        task2 =  Task.objects.create(author=user2, tasker=user1, content="task to me", type="task", status="yet", limit_date="2023-12-31")
        Comment.objects.create(author=user1, task=task1, content="test_comment")

        # When
        response = self.client.get(
            "/api/v1/tasks/my-group/"
        )
        data = response.json()

        # Then
        self.assertEqual(1, data[1]["counts"])
        self.assertEqual("task to me", data[0]["content"])

    def test_get_my_today_todo_list(self) -> None:
        # Given
        user = self.user_logged_in()
        [Task.objects.create(author=user, content=f"todo{i}", type="todo", status="doing", limit_date="2023-12-31") for i in range(1, 11)]

        # When
        response = self.client.get(
            "/api/v1/tasks/"
        )
        data = response.json()

        # Then
        self.assertEqual("todo10", data[0]["content"])




