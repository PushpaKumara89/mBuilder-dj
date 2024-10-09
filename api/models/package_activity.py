from django.db import models
from django.db.models import F
from safedelete import SOFT_DELETE
from typing import Union

from api.models.base_model import BaseModel


class PackageActivity(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'package_activities'
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                condition=models.Q(deleted__isnull=True),
                name='package_activity_unique_name_if_not_deleted'
            )
        ]

    name = models.CharField(max_length=255)
    activity_id = models.CharField(max_length=255, null=True)
    files = models.ManyToManyField('Media')
    description = models.TextField(null=True)
    description_image = models.ForeignKey('Media', on_delete=models.SET_NULL, null=True, related_name='package_activity_description_image')

    def get_asset_handover_count(self, project_id: Union[int, str]) -> int:
        if hasattr(self, 'asset_handovers'):
            return len(self.asset_handovers)
        else:
            return self.assethandover_set.filter(
                location_matrix__project_id=project_id,
                location_matrix__deleted__isnull=True,
                location_matrix__locationmatrixpackage__package_activity_id=F('package_activity_id'),
                location_matrix__locationmatrixpackage__enabled=True,
                location_matrix__locationmatrixpackage__deleted__isnull=True,
            ).count()

    def get_enabled_location_matrix_packages_count(self, project_id: Union[int, str]) -> int:
        if hasattr(self, 'enabled_location_matrix_packages'):
            return len(self.enabled_location_matrix_packages)
        else:
            return self.locationmatrixpackage_set.filter(
                enabled=True,
                deleted__isnull=True,
                location_matrix__project_id=project_id,
                location_matrix__deleted__isnull=True
            ).count()
