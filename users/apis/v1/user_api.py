from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.serializers import (
    UserInfoSerializer,
    UserDetailSerializer,
    WorkgroupSerializer,
    TodayListSerializer,
)

# 유저정보
class UserDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, context={"request":request})
        return Response(serializer.data)

    # 유저정보 수정 
    def put(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            serializer = UserDetailSerializer(updated_user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    #  유저가 가입한 그룹 삭제
    # def post(self, request):
    #     user = request.user
    #     group_pk = request.data['pk']
    #     try:
    #         workgroup = Workgroup.objects.get(pk=group_pk)
    #     except Workgroup.DoesNotExist:
    #         raise NotFound
    #     try:
    #         if workgroup.member == user:
    #             print(">>>here")
    #             return Response({"msg": "그룹 호스트는 탈퇴할 수 없습니다"})
    #         user.workgroups.remove(workgroup)
    #         return Response({"msg": "그룹에서 나오셨습니다"})
    #         # return Response(status=status.HTTP_200_OK)
    #     except Exception:
    #         raise ParseError("그룹 삭제 실패")


    # 유저삭제(회원탈퇴) - status: False
    def put(self, request):
        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)