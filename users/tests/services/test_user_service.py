from django.db import IntegrityError
from rest_framework.test import APITestCase
from users.models import User, Workgroup
from users.services.user_service import create_a_group_code, get_a_user


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

    # 그룹 생성
    def test_create_a_group(self) -> None:
        # Given
        user = User.objects.create(username="test", password="1234")
        group_code = "a123"

        # When
        workgroup = Workgroup.objects.create(group_code=group_code, member_id=user.pk)

        # Then
        self.assertEqual(group_code, workgroup.group_code)

    # 그룹코드 중복검증
    def test_group_code_should_be_only_one(self) -> None:
        # Given
        user = User.objects.create(username="test", password="1234")
        group_code = create_a_group_code("a123")
        Workgroup.objects.create(group_code=group_code, member_id=user.pk)

        # Expect
        with self.assertRaises(IntegrityError):
            Workgroup.objects.create(group_code=group_code, member_id=user.pk)

    # 내가 가입한 그룹 리스트
    def test_all_groups_list_I_joined(self) -> None:
        # Given
        user = User.objects.create(username="test", password="1234")
        user2 = User.objects.create(username="test2", password="1234")
        groups =  [Workgroup.objects.create(group_code=f"{i}", member_id=user2.pk) for i in range(1, 10)]
        user.workgroups.add(groups[0])

        # When
        my_group = user.workgroups.all()

        # Then
        self.assertEqual(1, len(my_group))
        

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