import random
from django.db.models import QuerySet
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

def get_members_in_group(group_pk: str) -> QuerySet[User]:
    return(
        Workgroup.objects.filter(pk=group_pk)
        .prefetch_related("users")
    )
