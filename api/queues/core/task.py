from django.db.models import Count

from api.models import Task


def delete_tasks(filters: dict) -> None:
    Task.objects.annotate(updates_count=Count('taskupdate')).filter(**filters, updates_count__gt=1).delete()


def restore_tasks(filters: dict) -> None:
    Task.deleted_objects.filter(**filters).undelete()
