from datetime import datetime, date
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied, ParseError
from rest_framework.permissions import  IsAuthenticated
from tasks.serializers import CreateTaskSerializer, TaskSerializer, TasksListSerializers

from tasks.services.task_service import get_date_list, get_my_group_task_list, get_my_today_todo_list, get_total_page
from tasks.models import Task
from users.models import User, Workgroup


"일정 작성한 날짜리스트 불러오기"
@api_view(('GET',))
@permission_classes([IsAuthenticated])
def date_list(request):
    try:
        page = request.query_params.get("page", 1)
        page = int(page)
    except ValueError:
        page = 1
    page_size = 5
    start = (page - 1) * page_size
    end = start + page_size
    return Response({"data": get_date_list(request.user.pk, start, end)})
    # total_page = get_total_page(request.user.pk, page_size)
    # return Response({"data": get_date_list(request.user.pk, start, end), "total_page": total_page})
    # a, b = get_date_list(request.user.pk, start, end)
    # return Response({'date':a, 'count': b})

# 날짜별 일정 페이지
@api_view(('GET',))
def page_list(request):
    page_size = 5
    total_page = get_total_page(request.user.pk, page_size)
    return Response({"data":total_page})


# 특정날짜의 모든 일정 가져오기
@api_view(('GET',))
def daily_tasks_list(request):
    if bool(request.query_params.dict()) == True:
        date = request.query_params.dict()["created_at"]
        all_tasks = Task.objects.filter(author=request.user, created_at__contains=date)
        serializer = TaskSerializer(
            all_tasks, many=True, context={"request": request}
        ) 
        return Response(serializer.data)
    else:
        raise NotFound
    

class MyGroupTasks(APIView):
    """나의 오늘 그룹 일정 (주고받은 일정 모두)""" 
    # 오늘의 그룹일정 불러오기 - test done
    def get(self, request):
        all_tasks = get_my_group_task_list(request.user.pk)
        serializer = TasksListSerializers(all_tasks, many=True)
        return Response(serializer.data)
    

class Tasks(APIView):
    """오늘 등록한 일정 불러오기"""
    
    # 오늘의 모든 일정 불러오기 - test done
    def get(self, request):
        all_tasks = get_my_today_todo_list(request.user.pk)
        serializer = TasksListSerializers(all_tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        # limit_date=null일경우 오늘 날짜로 등록
        if request.data.get("limit_date") == "" or request.data.get("limit_date") == None :
            limit = datetime.now()
            request.data["limit_date"] = limit
        # type이 task인 경우 status는 yet으로 변경
        if request.data.get("type") == "task":
            request.data["status"] = "yet"
            # group_pk 있는 경우 그룹 task
            group_pk = request.data["group_pk"]
            if group_pk:
                try:
                    group = Workgroup.objects.get(pk=group_pk)
                except Workgroup.DoesNotExist:
                    raise NotFound
            else:
                raise ParseError({"detail": "그룹을 선택해 주세요"})
        # tasker=null인경우 담당자는 본인
        if request.data.get("tasker") == "" or request.data.get("tasker") == None:
            tasker = request.user
        else:
            tasker_pk = request.data.get("tasker")
            try:
                tasker = User.objects.get(pk=tasker_pk)
            except User.DoesNotExist:
                raise NotFound({"detail":"상대 유저를 찾을 수 없습니다"})
        serializer = CreateTaskSerializer(data=request.data)

        if serializer.is_valid():
            if request.data.get("type") == "task":
                task = serializer.save(author=request.user, tasker=tasker, group=group)
            else:
                task = serializer.save(author=request.user)
            serializer = TasksListSerializers(task, context={"request": request})
            return Response(serializer.data)
        return Response(serializer.errors)


class TaskDetail(APIView):
    """
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
        # task = self.get_obj(pk)
        task = Task.objects.select_related("author", "tasker", "group").get(pk=pk)
        serializer = TaskSerializer(task, context={"request":request})
        return Response(serializer.data)

    # 일정 수정하기
    def put(self, request, pk):
        task = self.get_obj(pk)
        tasker_pk = request.data.get("tasker")
        group_pk = request.data.get("groupPk")
        type = request.data.get("type")
        if group_pk == "" or group_pk == None:
            new_group = task.group
        else:
            try:
                new_group = Workgroup.objects.get(pk=group_pk)
            except Workgroup.DoesNotExist:
                raise ParseError("Group not found")
        if tasker_pk == "" or tasker_pk == None:
            new_tasker = task.tasker
        else:
            try:
                new_tasker = User.objects.get(pk=tasker_pk)
            except User.DoesNotExist:
                raise ParseError("User not found")
        # 권한 검증
        if task.author != request.user:
            raise PermissionDenied
        serializer = CreateTaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
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

    # 일정 삭제하기
    def delete(self, request, pk):
        task = self.get_obj(pk)
        if task.author != request.user:
            raise PermissionDenied
        task.delete()
        return Response({"msg": "done"})


class GroupTasks(APIView):
    """그룹 멤버들의 오늘 일정 불러오기"""

    def get(self, request, pk):
        today = datetime.now().strftime("%Y-%m-%d")
        # 내가 속한 그룹 멤버들의 오늘 할일
        all_tasks = Task.objects.filter(group=pk, created_at__contains=today)
        serializer = TaskSerializer(all_tasks, many=True, context={"request":request})
        return Response(serializer.data)
    
# 오늘 일정 진행률
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