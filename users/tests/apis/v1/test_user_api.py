from tkinter.messagebox import NO
from rest_framework.test import APITestCase

from users.models import User, Workgroup

class TestUserAPI(APITestCase):

    def user_logged_in(self):
        user = User.objects.create(username="test_user")
        user.set_password("1234")
        user.save()
        self.user = user
        self.client.force_login(self.user)

    def test_edit_user_info(self) -> None:
        # Given
        self.user_logged_in()
        new_name = "new_name"

        # When
        response = self.client.put(
        "/api/v1/users/me",
        data = {
            "nickname": new_name
        },
            )

        data = response.json()

        # Then
        self.assertEqual(200, response.status_code)
        self.assertEqual(new_name, data["nickname"])


    def test_delete_a_user(self) -> None:
        # Given
        self.user_logged_in()

        # When
        response = self.client.put(
                "/api/v1/users/me",
                data = {
                    "status": False
                },
            )
        
        data = response.json()

        # Then
        self.assertEqual(False, data['status'])

class TestWorkgroupAPI(APITestCase):

    def user_logged_in(self):
        user = User.objects.create(username="test_user")
        user.set_password("1234")
        user.save()
        self.user = user
        self.client.force_login(self.user)
        return user
    
    def test_join_a_group(self) -> None:
        # Given
        user1 = self.user_logged_in()
        user2 = User.objects.create(username="test_user2", password="1234")
        workgroup = Workgroup.objects.create(group_code="a123", member_id=user2.pk)

        # When
        response = self.client.post(
            f"/api/v1/users/workgroups/{workgroup.pk}",
            data = {
                "member_pk": user1.pk
            }
        )

        data = response.json()

        # Then
        self.assertEqual(1, len(user1.workgroups.all()))
        self.assertEqual(workgroup.pk, data['workgroups'][0]['pk'])

    def test_leave_a_group(self) -> None:
        # Given
        user1 = self.user_logged_in()
        user2 = User.objects.create(username="test_user2", password="1234")
        workgroup = Workgroup.objects.create(group_code="a123", member_id=user2.pk)
        user1.workgroups.add(workgroup)

        # When
        response = self.client.put(
            "/api/v1/users/workgroups",
            data = {
                "pk": workgroup.pk
            }
        )

        data = response.json()

        # Then
        self.assertEqual("그룹에서 나오셨습니다", data['msg'])
        self.assertFalse(user1.workgroups.filter(pk=workgroup.pk).exists())
