import random
from sqlite3 import IntegrityError
from users.models import User, Workgroup


def get_a_user(pk: int) -> User:
    return User.objects.get(pk=pk)


def get_a_group(pk: int) -> Workgroup:
    return Workgroup.objects.get(pk=pk)

def create_a_group_code(group_code: str) -> str:
    while True:
        if Workgroup.objects.filter(group_code=group_code).exists():
            group_code = "a"
            group_code += str(random.randrange(100, 999))
            continue
        else:
            return group_code

