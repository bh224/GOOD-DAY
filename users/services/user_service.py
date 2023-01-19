from users.models import User, Workgroup


def get_a_user(pk: int) -> User:
    return User.objects.get(pk=pk)


def get_a_group(pk: int) -> Workgroup:
    return Workgroup.objects.get(pk=pk)