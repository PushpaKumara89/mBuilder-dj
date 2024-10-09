from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers import BaseManager
from api.models.queryset.package_queryset import PackageQueryset


class Package(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'packages'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                condition=models.Q(deleted__isnull=True),
                name='unique_name_if_not_deleted'
            )
        ]

    objects = BaseManager(PackageQueryset)

    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(db_index=True, default=0)
    package_activities = models.ManyToManyField(
        'PackageActivity',
        through='PackageMatrix',
        through_fields=('package', 'package_activity',)
    )
    projects = models.ManyToManyField(
        'Project',
        through='PackageMatrix',
        through_fields=('package', 'project',)
    )
