from django.db.models import Count, Q
from safedelete import HARD_DELETE

from api.models import Task


def hard_delete_tasks(task_filters: dict):
    Task.all_objects \
        .annotate(updates_count=Count('taskupdate')) \
        .filter(Q(**task_filters) & Q(updates_count__lt=2)) \
        .delete(HARD_DELETE)
