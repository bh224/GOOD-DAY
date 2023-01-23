import random
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.serializers import (
    UserInfoSerializer,
    UserDetailSerializer,
    WorkgroupSerializer,
    TodayListSerializer,
)
from users.models import User, Workgroup
from users.services.user_service import create_a_group_code, get_a_group



class UserDetail(APIView):
    """ 유저정보 """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, context={"request":request})
        return Response(serializer.data)

    # 유저정보 수정  & 회원탈퇴 (status=False) - test done
    def put(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            serializer = UserDetailSerializer(updated_user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        

class WorkGroupList(APIView):
    """유저가 가입한 그룹 관련"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 모든 그룹 불러오기 (?all)
        if bool(request.query_params.dict()) == True:
            groups = Workgroup.objects.all()
            serializer = WorkgroupSerializer(groups, many=True, context={"request":request})
            return Response(serializer.data)
        # 유저가 속한 그룹 불러오기
        user = request.user
        groups = user.workgroups.all()
        serializer = WorkgroupSerializer(groups, many=True, context={"request":request})
        return Response(serializer.data)

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