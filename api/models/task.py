from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.indexes import Index
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers import BaseManager, BaseAllManager
from api.models.queryset.task_queryset import TaskQueryset


class Task(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = BaseManager(TaskQueryset)
    all_objects = BaseAllManager(TaskQueryset)

    class Meta(BaseModel.Meta):
        db_table = 'tasks'
        constraints = [
            UniqueConstraint(
                fields=['package_activity', 'package_activity_task', 'location_matrix'],
                name='tasks_uniqueness',
                condition=models.Q(deleted__isnull=True),
            ),
            Index(
                fields=('building', 'id', 'project_id'),
                name='tasks_building_id_project_index',
                condition=models.Q(~models.Q(status='not_applicable'), deleted__isnull=True),
            ),
            Index(
                fields=('level', 'id', 'project_id'),
                name='tasks_level_id_project_index',
                condition=models.Q(~models.Q(status='not_applicable'), deleted__isnull=True),
            ),
            Index(
                fields=('area', 'id', 'project_id'),
                name='tasks_area_id_project_index',
                condition=models.Q(~models.Q(status='not_applicable'), deleted__isnull=True),
            ),
            Index(
                fields=('package', 'id', 'project_id'),
                name='tasks_package_id_project_index',
                condition=models.Q(~models.Q(status='not_applicable'), deleted__isnull=True),
            ),
            Index(
                fields=('created_at', 'id', 'project_id'),
                name='tasks_created_at_id_project_index',
                condition=models.Q(~models.Q(status='not_applicable'), deleted__isnull=True),
            ),
            Index(
                fields=('updated_at', 'id', 'project_id'),
                name='tasks_updated_at_id_project_index',
                condition=models.Q(~models.Q(status='not_applicable'), deleted__isnull=True),
            ),
            Index(
                fields=('status', 'id', 'project_id'),
                name='tasks_status_id_project_index',
                condition=models.Q(~models.Q(status='not_applicable'), deleted__isnull=True),
            ),
            Index(
                fields=('project_id', 'user_id'),
                name='tasks_project_id_user_id_index',
                condition=models.Q(deleted__isnull=True)
            ),
        ]

    class Statuses(models.TextChoices):
        ACCEPTED = 'accepted', _('Accepted')
        NOT_APPLICABLE = 'not_applicable', _('Not Applicable')
        NOT_VERIFIED = 'not_verified', _('Not Verified')
        OUTSTANDING = 'outstanding', _('Outstanding')
        PART_COMPLETE = 'part_complete', _('Part Complete')
        REJECTED = 'rejected', _('Rejected')

    package_activity = models.ForeignKey('PackageActivity', on_delete=models.CASCADE)
    package_activity_task = models.ForeignKey('PackageActivityTask', on_delete=models.CASCADE)
    location_matrix = models.ForeignKey('LocationMatrix', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=Statuses.choices, default=Statuses.OUTSTANDING.value)
    date_of_approval = models.DateTimeField(null=True)
    local_id = models.CharField(null=True, blank=True, default=None, max_length=255)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True)
    package = models.ForeignKey('Package', on_delete=models.SET_NULL, null=True)
    building = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
