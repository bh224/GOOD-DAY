from django.db.models import F
from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.status import HTTP_204_NO_CONTENT

from tasks.models import Task, Comment
from tasks.serializers import CreateCommentSerializer, CommentSerializer
from tasks.services.comment_service import get_comments_belongs_to_a_task




class Comments(APIView):
    """task에 달린 코멘트 가져오기, 작성하기"""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_obj(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        task = self.get_obj(pk)
        all_comments = get_comments_belongs_to_a_task(pk)
        # all_comments = Comment.objects.filter(task=task).select_related("author").select_related("task")
        serializer = CommentSerializer(all_comments, many=True)
        return Response(serializer.data)

    # 코멘트 작성하기
    def post(self, request, pk):
        task = self.get_obj(pk)
        serializer = CreateCommentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    comment = serializer.save(task=task, author=request.user)
                    if Task.objects.filter(pk=pk).update(comment_cnt=F("comment_cnt") + 1):
                        serializer = CommentSerializer(comment)
                        return Response(serializer.data)
                    else:
                        raise ParseError({"Try Again"})
            except Exception:
                raise ParseError({"다시 시도해 주세요"})
        else:
            return Response(serializer.errors)
        

class CommentDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_task(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise NotFound

    def get_comment(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except:
            raise NotFound

    # 코멘트 상세 불러오기
    def get(self, request, pk, comment_id):
        comment = self.get_comment(comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    # 코멘트 수정하기
    def put(self, request, pk, comment_id):
        task = self.get_task(pk)
        comment = self.get_comment(comment_id)
        serializer = CreateCommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            updated_comment = serializer.save(task=task, author=request.user)
            serializer = CommentSerializer(updated_comment)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    # 코멘트 삭제하기
    def delete(self, request, pk, comment_id):
        comment = self.get_comment(comment_id)
        if comment.author != request.user:
            raise ParseError("접근권한이 없습니다")
        try:
            with transaction.atomic():
                comment.delete()
                Task.objects.get(pk=999)
                Task.objects.filter(pk=pk).update(comment_cnt=F("comment_cnt") - 1)
        except Exception:
            raise ParseError({"다시 시도해 주세요"})
        return Response(status=HTTP_204_NO_CONTENT)