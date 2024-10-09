from django.db.models import Count, Q
from safedelete import HARD_DELETE

from api.models import Task


def package_activity_tasks_hard_delete_related_qct(task_filters: dict, task_exclude_filters: dict = None):
    Task.all_objects\
        .annotate(updates_count=Count('taskupdate'))\
        .filter(Q(**task_filters) & Q(updates_count__lt=2))\
        .exclude(**task_exclude_filters)\
        .delete(HARD_DELETE)
