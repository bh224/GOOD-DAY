from rest_framework.test import APITestCase
from users.models import User, Workgroup
from users.services.user_service import get_a_user


class TestUserService(APITestCase):

    # 유저정보변경
    def test_edit_use_infor(self) -> None:
        # Given
        new_name = "new_name"
        user = User.objects.create(username="test", password="1234", nickname="test_name")
        
        # When
        User.objects.filter(pk=user.pk).update(nickname=new_name)
        result_user = get_a_user(user.pk)

        # Then
        self.assertEqual(new_name, result_user.nickname)

    # 유저삭제(회원탈퇴) -> status: False
    def test_delete_a_user(self) -> None:
        # Given
        user = User.objects.create(username="test", password="1234")
        
        # When
        User.objects.filter(pk=user.pk).update(status=False)
        result_user = get_a_user(user.pk)

        # Then
        self.assertEqual(False, result_user.status)

class TestWorkgroupServie(APITestCase):

    # 그룹 가입
    def test_join_a_group(self) -> None:
        # Given
        user = User.objects.create(username="test_user", password="1234")
        user1 = User.objects.create(username="test_user1", password="1234")
        workgroup = Workgroup.objects.create(group_code="a123", member_id=user1.pk)

        # When
        user.workgroups.add(workgroup)

        # Then
        self.assertTrue(user.workgroups.filter(pk=workgroup.pk).exists())
        self.assertIn(Workgroup.objects.get(pk=workgroup.pk), user.workgroups.all())

    # 그룹 탈퇴
    def test_leave_a_group(self) -> None:
        # Given
        user = User.objects.create(username="test_user", password="1234")
        workgroup = Workgroup.objects.create(group_code="a123", member_id=user.pk)
        user.workgroups.add(workgroup)

        # When
        user.workgroups.remove(workgroup)

        # Then
        self.assertFalse(user.workgroups.filter(pk=workgroup.pk).exists())