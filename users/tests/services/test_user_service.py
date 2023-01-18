from rest_framework.test import APITestCase
from users.models import User
from users.services.user_service import get_a_user


class TestUserService(APITestCase):
    # 유저삭제(회원탈퇴) -> status: False
    def test_delete_a_user(self) -> None:
        # Given
        user = User.objects.create(username="test", password="1234")
        
        # When
        User.objects.filter(pk=user.pk).update(status=False)
        result_user = get_a_user(user.pk)

        # Then
        self.assertEqual(False, result_user.status)