import random
import math
from typing import Tuple, List
from django.db.models import QuerySet, Prefetch
from users.models import User, Workgroup


def get_a_user(pk: int) -> User:
    return User.objects.get(pk=pk)


# def get_a_group(pk: int) -> Workgroup:
#     return Workgroup.objects.get(pk=pk)

# 내가 가입한 그룹 불러오기 (5개씩) - 메인페이지 mygroup 탭
# def get_my_group_list(filter: int, user_pk: int, offset: int, limit: int) -> QuerySet:
#     # user = User.objects.get(pk=user_pk)
#     # my_groups = user.workgroups.all()[offset:limit] 
#     # my_groups = User.objects.prefetch_related("workgroups").filter(pk=user_pk)
#     my_groups = User.objects.prefetch_related(Prefetch("workgroups")).get(pk=user_pk).workgroups.all()
#     # my_groups = User.objects.filter(pk=1).prefetch_related("workgroups").get().workgroups.all()
#     # my_groups = User.objects.filter(pk=1).prefetch_related(Prefetch("workgroups", queryset=Workgroup.objects.all())).get().workgroups.all()
#     # my_groups = Workgroup.objects.prefetch_related(Prefetch("users", queryset=User.objects.filter(pk=user_pk), to_attr="mygroup"))
#     if filter:
#         return my_groups
#     else:
#         return my_groups[offset:limit]



# def create_a_group_code(group_code: str) -> str:
#     while True:
#         if Workgroup.objects.filter(group_code=group_code).exists():
#             group_code = "a"
#             group_code += str(random.randrange(100, 999))
#             continue
#         else:
#             return group_code

def get_members_in_group(group_pk: str) -> QuerySet[User]:
    return(
        Workgroup.objects.filter(pk=group_pk)
        .prefetch_related("users")
    )



#  모든 그룹 불러오기 - 메인페이지 그룹탭
# def get_all_group_list(user_pk:int, offset: int, limit: int) -> QuerySet:
#     # all_groups = Workgroup.objects.prefetch_related(Prefetch("users", queryset=User.objects.filter(pk=user_pk)))
#     all_groups = Workgroup.objects.prefetch_related("users")
#     return all_groups[offset:limit]


# def get_total_group_page(user_pk: int, offset: int) -> Tuple[List[str], List[str]] :
#     user = User.objects.get(pk=user_pk)
#     my_total_page = math.ceil(
#         user.workgroups.count() / offset
#     )
#     all_total_page = math.ceil(Workgroup.objects.all().count() / offset)
#     return ([i for i in range(1, my_total_page + 1)], [i for i in range(1, all_total_page + 1)])