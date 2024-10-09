from django.db import models
from django.db.models import Q
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers import BaseDeletedManager, BaseAllManager, BaseManager
from api.models.queryset.asset_handover_queryset import AssetHandoverQueryset


class AssetHandover(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = BaseManager(AssetHandoverQueryset)
    deleted_objects = BaseDeletedManager(AssetHandoverQueryset)
    all_objects = BaseAllManager(AssetHandoverQueryset)

    class Meta(BaseModel.Meta):
        db_table = 'asset_handovers'
        indexes = [
            models.Index(
                fields=('project', 'package_activity', 'deleted'),
                name='asset_handovers_ihe6oz_index'
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=('package_activity', 'location_matrix',),
                name='asset_handover_unique',
                condition=Q(deleted__isnull=True)
            )
        ]

    package_activity = models.ForeignKey('PackageActivity', on_delete=models.CASCADE)
    location_matrix = models.ForeignKey('LocationMatrix', on_delete=models.CASCADE)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True)

    def get_related_documents(self, filters: dict, documents_prefetch=None):
        if documents_prefetch is None:
            documents_prefetch = []

        return list(self.assethandoverdocument_set.prefetch_related(
            *documents_prefetch
        ).filter(**filters))
