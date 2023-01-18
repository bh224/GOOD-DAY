from rest_framework.test import APITestCase

from users.models import User

class TestUserAPI(APITestCase):

    def user_logged_in(self):
        user = User.objects.create(username="test_user")
        user.set_password("1234")
        user.save()
        self.user = user
        self.client.force_login(self.user)


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