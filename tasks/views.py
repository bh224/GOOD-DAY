from datetime import date
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from users.models import User
from .models import Task, Comment
from .serializers import TaskSerializer, TasksListSerializers, CommentSerializer
from tasks import serializers

# Create your views here.
class Tasks(APIView):
    """
    GETT /api/v1/tasks
    : 나와 관련된 모든 task를 불러오기 (내가 등록한 task, 남이 나에게 부여한 task, 내가 남에게 부여한 task)
    """
    
    def get(self, request):
        # print(request.user.pk)
        all_tasks = Task.objects.filter(
            Q(author=request.user) | Q(tasker=request.user)
        ).order_by('-created_at')
        serializer = TasksListSerializers(
            all_tasks, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        # drf에서 post 요청 보낼 때는 author:1, tasker:2 이런식으로 보낸다 하지만 이대로는 저장 안됨
        # 시리얼라이저에서 author & tasker는 read_only 로 해놔서 request.data로 안 보내도 된다

        # limit_date=null일경우 오늘 날짜로 등록
        if request.data.get("limit_date") == None:
            limit = date.today().isoformat()
            request.data["limit_date"] = limit
        
        # type이 task인 경우 status는 yet으로 변경
        if request.data.get("type") == "task":
            request.data["status"] = "yet"

        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            # 내가 등록한 내 일정인 경우 tasker = 나
            try:
                tasker_pk = request.data.get("tasker")
                # print("tasker_pk", tasker_pk)
                tasker = User.objects.get(pk=tasker_pk)
            except User.DoesNotExist:
                tasker = request.user
            task = serializer.save(author=request.user, tasker=tasker)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        return Response(serializer.errors)


class TaskDetail(APIView):
    """
    api/v1/tasks/1
    상세일정 불러오기/수정하기/삭제하기
    """

    # 특정 일정 불러오기
    def get_obj(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        task = self.get_obj(pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_obj(pk)
        # 일정작성자만 수정가능
        if task.author != request.user:
            raise PermissionDenied
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            print("valid")
            tasker_pk = request.data.get("tasker")
            new_type = request.data.get("type")
            # 새롭게 들어온 tasker가 있으면 일단 검증
            if tasker_pk:
                try:
                    tasker = User.objects.get(pk=tasker_pk)
                except User.DoesNotExist:
                    raise ParseError("User not found")
            # tasker가 없는 경우에만(내 일정인 경우만) tasker 지정불가, type만 변경가능
            if task.tasker == None or task.tasker == request.user:
                if tasker_pk:
                    raise ParseError("나의 일정에는 다른 유저를 담당자로 지정할 수 없습니다")
                else:
                    new_task = serializer.save()
                    return Response(TaskSerializer(new_task).data)
            # 현재 tasker가 있는경우
            else:
                if new_type:
                    raise ParseError("담당자가 있는 일정은 타입을 변경할 수 없습니다")
                else:
                    if tasker_pk:
                        new_task = serializer.save(tasker=tasker)
                        return Response(TaskSerializer(new_task).data)
                    else:
                        new_task = serializer.save()
                        return Response(TaskSerializer(new_task).data)

        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        task = self.get_obj(pk)
        if task.author != request.user:
            raise PermissionDenied
        task.delete()
        return Response({"msg": "done"})


class Comments(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_obj(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        task = self.get_obj(pk)
        all_comments = task.comments.all()
        serializer = CommentSerializer(all_comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        task = self.get_obj(pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(task=task, author=request.user)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
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

    def get(self, request, pk, comment_id):
        comment = self.get_comment(comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk, comment_id):
        task = self.get_task(pk)
        comment = self.get_comment(comment_id)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            updated_comment = serializer.save(task=task, author=request.user)
            serializer = CommentSerializer(updated_comment)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk, comment_id):
        comment = self.get_comment(comment_id)
        if comment.author != request.user:
            raise ParseError("접근권한이 없습니다")
        comment.delete()
        return Response(status=HTTP_204_NO_CONTENT)
