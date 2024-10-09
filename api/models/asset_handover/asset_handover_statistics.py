from django.contrib.auth.models import Group
from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel

from api.models.managers.asset_handover_statistics_manager import AssetHandoverStatisticsManager


class AssetHandoverStatistics(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = AssetHandoverStatisticsManager()

    class Meta(BaseModel.Meta):
        db_table = 'asset_handover_statistics'

    accepted_count = models.IntegerField(default=0)
    contested_count = models.IntegerField(default=0)
    in_progress_count = models.IntegerField(default=0)
    removed_count = models.IntegerField(default=0)
    requested_approval_rejected_count = models.IntegerField(default=0)
    requesting_approval_count = models.IntegerField(default=0)
    required_files_count = models.IntegerField(default=0)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    asset_handover_document = models.ForeignKey('AssetHandoverDocument', on_delete=models.CASCADE)
