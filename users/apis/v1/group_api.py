import random
from django.db import transaction
from django.db.models import Prefetch
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ParseError, NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.serializers import (
    TestWorkgroupSerializer,
    WorkgroupIncludingMembers,
    WorkgroupSerializer,
    SimpleWorkgroupSerializer,
    UserDetailSerializer
)
from users.models import User, Workgroup
from users.services.group_service import create_a_group_code, get_a_group, get_all_group_list, get_my_group_list, get_total_group_page


# GET /api/v1/users/workgroups?page=all
class WorkGroupList(APIView):
    """유저가 가입한 그룹 관련"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # # 모든 그룹 불러오기 (?all)
        # if bool(request.query_params.dict()) == True:
        #     groups = Workgroup.objects.all()
        #     serializer = WorkgroupSerializer(groups, many=True, context={"request":request})
        #     return Response(serializer.data)
        # # 유저가 속한 그룹 불러오기
        # user = request.user
        # groups = user.workgroups.all()
        # serializer = WorkgroupSerializer(groups, many=True, context={"request":request})
        # return Response(serializer.data)

        # 유저가 속한 그룹 전체 불러오기 - 메인페이지 셀렉트, todo 업로드, 수정 모달
        if request.query_params.get("page") == "all":
            user = request.user
            # groups = user.workgroups.all()
            # serializer = WorkgroupSerializer(groups, many=True, context={"request":request})
            mygroups = get_my_group_list(1, request.user.pk, 0, 0)
            serializer = WorkgroupIncludingMembers(mygroups, many=True, context={"request":request})
            return Response(serializer.data)
        
        # 유저가 속한 그룹 5개씩 불러오기 - 메인페이지  Mygroup
        # GET /api/v1/users/workgroups?page={page}
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = 5
        start = (page - 1) * page_size
        end = start + page_size
        mygroups = get_my_group_list(0, request.user.pk, start, end)
        serializer = TestWorkgroupSerializer(mygroups, many=True, context={"request":request})
        return Response(serializer.data)
        # return Response({"data": get_my_group_list(request.user.pk, start, end)})

    # 그룹 생성 - test done
    def post(self, request):
        user = request.user
        code = "a"
        code += str(random.randrange(100, 999))
        code = create_a_group_code(code)
        request.data['group_code'] = code
        serializer = WorkgroupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    workgroup = serializer.save(member=user)
                    user.workgroups.add(workgroup)
                    serializer = WorkgroupSerializer(workgroup,  context={'request': request})
                    return Response(serializer.data)
            except Exception:
                raise ParseError('그룹생성실패')
        else:
            return Response(serializer.errors)
        
    #  그룹 탈퇴  - test done
    def put(self, request):
        user = request.user
        group_pk = request.data['pk']
        try:
            workgroup = get_a_group(group_pk)
        except Workgroup.DoesNotExist:
            raise NotFound
        try:
            if workgroup.member == user:
                return Response({"msg": "그룹 호스트는 탈퇴할 수 없습니다"})
            user.workgroups.remove(workgroup)
            return Response({"msg": "그룹에서 나오셨습니다"})
        except Exception:
            raise ParseError("Please Try Again")
        


class WorkGroupDetail(APIView):
    def get_group(self, pk):
        try:
            return Workgroup.objects.get(pk=pk)
        except Workgroup.DoesNotExist:
            raise NotFound

    # 특정 그룹 불러오기
    def get(self, request, pk):
        # workgroup = self.get_group(pk)
        workgroup = Workgroup.objects.prefetch_related("users").get(pk=pk)
        serializer = WorkgroupSerializer(workgroup, context={"request":request})
        return Response(serializer.data)

    # 그룹에 멤버 추가 (나 or 다른유저) - test done
    def post(self, request, pk):
        workgroup = self.get_group(pk)
        member_pk = request.data["member_pk"]
        if member_pk != '':
            try:
                member = User.objects.get(pk=member_pk)
            except User.DoesNotExist:
                raise NotFound
        else:
            member = request.user
        try:
            member.workgroups.add(workgroup)
            serializer = UserDetailSerializer(member, context={"request": request})
            return Response(serializer.data)
        except Exception:
            raise ParseError(status.HTTP_400_BAD_REQUEST)

    # 그룹명 수정
    def put(self, request, pk):
        workgroup = self.get_group(pk)
        if workgroup.member != request.user:
            raise PermissionDenied
        serializer = WorkgroupSerializer(workgroup, data=request.data, partial=True)
        if serializer.is_valid():
            workgroup = serializer.save()
            serializer = WorkgroupSerializer(workgroup, context={"request": request})
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    # 그룹삭제
    def delete(self, request, pk):
        workgroup = self.get_group(pk)
        if workgroup.member != request.user:
            raise PermissionDenied
        workgroup.delete()
        return Response({"msg": "그룹삭제완료"})

# 내가 가입한 그룹 페이지 리스트
@api_view(('GET',))
@permission_classes([IsAuthenticated])
def page_lists(request):
    page_size = 5
    total_page = get_total_group_page(request.user.pk, page_size)
    return Response({"mygroup":total_page[0], "allgroup":total_page[1]})

# 모든그룹 불러오기 GET /api/v1/users/workgroups/all
@api_view(('GET',))
def get_all_groups(request):
    try:
        page = request.query_params.get("page", 1)
        page = int(page)
    except ValueError:
        page = 1
    page_size = 5
    start = (page - 1) * page_size
    end = start + page_size
    mygroups = get_all_group_list(request.user.pk, start, end)
    serializer = SimpleWorkgroupSerializer(mygroups, many=True, context={"request":request})
    return Response(serializer.data)


# 그룹 내 멤버 추가 시 username 검색
@api_view(('POST',))
def check_username_in_group(request):
    username = request.data.get("username")
    group_pk = request.data.get("pk")
    print(username, group_pk)
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise NotFound
    try:
        group = Workgroup.objects.get(pk=group_pk)
    except Workgroup.DoesNotExist:
        raise NotFound
    if group.users.filter(username=username).exists():
        return Response({"detail": "이미 그룹에 참여중 입니다"})
    else:
        data = {
            "pk": user.pk,
            "username": user.username,
            "nickname": user.nickname
        }
        return Response(data)

