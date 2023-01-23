from datetime import datetime, date
from lib2to3.pgen2.parse import ParseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from tasks.serializers import TaskSerializer, TasksListSerializers

from tasks.services.task_service import get_date_list, get_my_group_task_list, get_my_today_todo_list, get_total_page
from tasks.models import Task
from users.models import User, Workgroup


"내가 작성한 일정 불러오기"
@api_view(('GET',))
def date_list(request):
    try:
        page = request.query_params.get("page", 1)
        page = int(page)
    except ValueError:
        page = 1
    page_size = 5
    start = (page - 1) * page_size
    end = start + page_size
    total_page = get_total_page(request.user.pk, page_size)
    return Response({"data": get_date_list(request.user.pk, start, end), "total_page": total_page})
    # a, b = get_date_list(request.user.pk, start, end)
    # return Response({'date':a, 'count': b})


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
        if request.data.get("limit_date") == "":
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
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            if request.data.get("type") == "task":
                task = serializer.save(author=request.user, tasker=tasker, group=group)
            else:
                task = serializer.save(author=request.user)
            serializer = TaskSerializer(task, context={"request": request})
            return Response(serializer.data)
        return Response(serializer.errors)
