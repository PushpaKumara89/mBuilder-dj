from django.contrib.auth.models import Group
from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers.package_handover_statistics_manager import PackageHandoverStatisticsManager


class PackageHandoverStatistics(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'package_handover_statistics'

    objects = PackageHandoverStatisticsManager()

    in_progress_count = models.IntegerField(default=0)
    removed_count = models.IntegerField(default=0)
    contested_count = models.IntegerField(default=0)
    accepted_count = models.IntegerField(default=0)
    requesting_approval_count = models.IntegerField(default=0)
    requested_approval_rejected_count = models.IntegerField(default=0)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    package_handover_document = models.ForeignKey('PackageHandoverDocument', on_delete=models.CASCADE, null=True)
