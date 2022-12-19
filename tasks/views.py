from datetime import date, datetime
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import api_view
from users.models import User, Workgroup
from .models import Task, Comment
from .serializers import TaskSerializer, TasksListSerializers, CommentSerializer
from tasks import serializers

# Create your views here.
class Tasks(APIView):
    """
    GET /api/v1/tasks
    : 오늘 등록한 일정 불러오기
    """

    def get(self, request):
        # print(request.user.pk)
        # if bool(request.query_params.dict()) == False:
        #     print(">>>here")
        today = datetime.now().strftime("%Y-%m-%d")
        all_tasks = Task.objects.filter(
            author=request.user,
            created_at__contains=today,
            # created_at__contains=now.date(),
        ).order_by("-created_at")
        serializer = TasksListSerializers(all_tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        # drf에서 post 요청 보낼 때는 author:1, tasker:2 이런식으로 보낸다 하지만 이대로는 저장 안됨
        # 시리얼라이저에서 author & tasker는 read_only 로 해놔서 request.data로 안 보내도 된다
        # print(request.data)
        # limit_date=null일경우 오늘 날짜로 등록
        if request.data.get("limit_date") == "":
            limit = date.today().isoformat()
            request.data["limit_date"] = limit
        # type이 task인 경우 status는 yet으로 변경
        if request.data.get("type") == "task":
            request.data["status"] = "yet"
            # tasker=null인경우 담당자는 본인
            group_pk = request.data["group_pk"]
            if group_pk:
                try:
                    group = Workgroup.objects.get(pk=group_pk)
                except Workgroup.DoesNotExist:
                    raise NotFound
        if request.data.get("tasker") == "" or request.data.get("tasker") == None:
            tasker = request.user
        else:
            tasker_pk = request.data.get("tasker")
            # print("tasker_pk", tasker_pk)
            tasker = User.objects.get(pk=tasker_pk)
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            # 내가 등록한 내 일정인 경우 tasker = 나
            if request.data.get("type") == "task":
                task = serializer.save(author=request.user, tasker=tasker, group=group)
            else:
                task = serializer.save(author=request.user)
            serializer = TaskSerializer(task, context={"request": request})
            return Response(serializer.data)
        return Response(serializer.errors)


class TasksToMe(APIView):
    def get(self, request):
        now = datetime.now()
        all_tasks = Task.objects.filter(
            tasker=request.user,
            created_at__contains=date(now.year, now.month, now.day),
        ).order_by("-created_at")
        serializer = TasksListSerializers(all_tasks, many=True)
        return Response(serializer.data)


class AllTasks(APIView):
    task_dates = set()

    def get(self, request):
        # 쿼리파라미터로 받아온 날짜(작성일)
        if bool(request.query_params.dict()) == True:
            date = request.query_params.dict()["created_at"]
            all_tasks = Task.objects.filter(created_at__contains=date)
            serializer = TaskSerializer(
                all_tasks, many=True, context={"request": request}
            )
            return Response(serializer.data)
        # 쿼리파라미터 없을 시 작성일 리스트 반환
        all_tasks = Task.objects.filter(
            Q(author=request.user) | Q(tasker=request.user)
        ).values("created_at")
        for task in all_tasks:
            self.task_dates.add(task["created_at"].strftime("%Y-%m-%d"))
        return Response({"data": sorted(list(self.task_dates), reverse=True)})


class TaskDetail(APIView):
    """
    api/v1/tasks/1
    상세일정 불러오기/수정하기/삭제하기
    """

    permission_classes = [IsAuthenticated]
    # 일정  상세 불러오기
    def get_obj(self, pk):
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        task = self.get_obj(pk)
        serializer = TaskSerializer(task, context={"request":request})
        return Response(serializer.data)

    def put(self, request, pk):
        print(request.data)
        task = self.get_obj(pk)
        tasker_pk = request.data.get("tasker")
        group_pk = request.data.get("groupPk")
        type = request.data.get("type")
        print("pk", group_pk, tasker_pk)
        if group_pk == "":
            new_group = task.group
            print(new_group)
        else:
            try:
                print("grouppk 있음")
                new_group = Workgroup.objects.get(pk=group_pk)
            except Workgroup.DoesNotExist:
                raise ParseError("Group not found")
        if tasker_pk == "":
            new_tasker = task.tasker
            print(new_tasker)
        else:
            try:
                print("taskerpk 있음")
                new_tasker = User.objects.get(pk=tasker_pk)
            except User.DoesNotExist:
                raise ParseError("User not found")
        # 권한 검증
        if task.author != request.user:
            raise PermissionDenied
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            print(">>>here")
            if type == "task":
                new_task = serializer.save(group=new_group, tasker=new_tasker)
                serializer = TaskSerializer(new_task, context={"request":request})
                return Response(serializer.data)
            else:
                new_task = serializer.save()
                serializer = TaskSerializer(new_task, context={"request":request})
                return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        task = self.get_obj(pk)
        if task.author != request.user:
            raise PermissionDenied
        task.delete()
        return Response({"msg": "done"})


class GroupTasks(APIView):
    def get(self, request, pk):
        today = datetime.now().strftime("%Y-%m-%d")
        # 내가 속한 그룹 멤버들의 오늘 할일
        all_tasks = Task.objects.filter(group=pk, created_at__contains=today)
        serializer = TaskSerializer(all_tasks, many=True, context={"request":request})
        return Response(serializer.data)


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
        print(task)
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
        print(">>>>>here")
        comment = self.get_comment(comment_id)
        print(comment)
        if comment.author != request.user:
            raise ParseError("접근권한이 없습니다")
        comment.delete()
        return Response(status=HTTP_204_NO_CONTENT)

@api_view(('GET',))
def task_counts(request):
    today = datetime.now().strftime("%Y-%m-%d")
    all_tasks = Task.objects.filter(
        (Q(author=request.user) | Q(tasker=request.user)), created_at__contains=today
    )
    done_tasks = Task.objects.filter(
        (Q(author=request.user) | Q(tasker=request.user)),
        created_at__contains=today,
        status="done",
    )
    data = {
        "all": all_tasks.count(),
        "done": done_tasks.count(),
    }
    return Response(data)
