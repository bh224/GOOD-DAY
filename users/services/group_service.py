import random
import math
from typing import Tuple, List
from django.db.models import QuerySet, Prefetch
from users.models import User, Workgroup


def get_a_group(pk: int) -> Workgroup:
    return Workgroup.objects.get(pk=pk)

# 내가 가입한 그룹 불러오기 (5개씩) - 메인페이지 mygroup 탭
def get_my_group_list(filter: int, user_pk: int, offset: int, limit: int) -> QuerySet:
    user = User.objects.get(pk=user_pk)
    my_groups = user.workgroups.all() 
    # my_groups = Workgroup.objects.prefetch_related(Prefetch("member__workgroups"))
    # my_groups = User.objects.prefetch_related(Prefetch("workgroups")).get(pk=user_pk).workgroups.all()
    # my_groups = User.objects.prefetch_related(Prefetch("workgroups", queryset=User.objects.filter(pk=user_pk))).all()
    # my_groups = User.objects.filter(pk=1).prefetch_related(Prefetch("workgroups", queryset=Workgroup.objects.all())).get().workgroups.all()
    # my_groups = Workgroup.objects.prefetch_related(Prefetch("user_mygroups_set", queryset=User_Mygroups.objects.filter(user_id=user_pk)) )
    # my_groups = my_groups.workgroups.all()
    
    if filter:
        return my_groups
    else:
        return my_groups[offset:limit]
    
#  모든 그룹 불러오기 - 메인페이지 그룹탭
def get_all_group_list(user_pk:int, offset: int, limit: int) -> QuerySet:
    all_groups = Workgroup.objects.prefetch_related("users")
    # all_groups = Workgroup.objects.all()

    return all_groups[offset:limit]


def create_a_group_code(group_code: str) -> str:
    while True:
        if Workgroup.objects.filter(group_code=group_code).exists():
            group_code = "a"
            group_code += str(random.randrange(100, 999))
            continue
        else:
            return group_code
        
def get_total_group_page(user_pk: int, offset: int) -> Tuple[List[str], List[str]] :
    user = User.objects.get(pk=user_pk)
    my_total_page = math.ceil(
        user.workgroups.count() / offset
    )
    all_total_page = math.ceil(Workgroup.objects.all().count() / offset)
    return ([i for i in range(1, my_total_page + 1)], [i for i in range(1, all_total_page + 1)])