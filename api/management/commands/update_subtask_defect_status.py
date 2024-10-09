from django.core.management.base import BaseCommand
from django.db.models import Q, F

from api.models import Subtask


class Command(BaseCommand):
    help = "Update is_defect field for open subtasks."

    def handle(self, *args, **options):
        Subtask.all_objects.exclude(Q(status=Subtask.Status.CLOSED) |
                                    Q(created_at__lt=F('task__location_matrix__project__completion_date')) |
                                    Q(is_defect=True)).\
                            update(is_defect=True)
