from tasks.models import Task


def get_a_task(pk: int) -> Task:
    return Task.objects.get(pk=pk)