from django.db import models
from django.db.models import UniqueConstraint, Q
from safedelete import SOFT_DELETE

from api.models import PackageActivity
from api.models.base_model import BaseModel


class PackageActivityTask(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta:
        db_table = 'package_activity_tasks'
        ordering = ['order', 'id']
        constraints = [
            UniqueConstraint(
                fields=['package_activity', 'description'],
                condition=Q(deleted__isnull=True),
                name='package_activity_task_unique_description_if_not_deleted'
            ),
            UniqueConstraint(
                fields=['package_activity', 'is_default_for_subtask'],
                condition=Q(deleted__isnull=True, is_default_for_subtask=True),
                name='package_activity_task_unique_default_for_subtask_if_not_deleted'
            )
        ]
    
    description = models.TextField()
    is_photo_required = models.BooleanField(default=False)
    is_not_applicable_status_by_default = models.BooleanField(default=True)
    order = models.PositiveIntegerField(db_index=True, default=0)
    package_activity = models.ForeignKey(PackageActivity, on_delete=models.CASCADE)
    photo_requirement_comment = models.TextField()
    is_default_for_subtask = models.BooleanField(default=False)
