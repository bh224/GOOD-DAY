from users.models import User


def get_a_user(pk: int) -> User:
    return User.objects.get(pk=pk)
