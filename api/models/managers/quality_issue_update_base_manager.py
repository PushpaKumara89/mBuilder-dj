from api.models.managers import BaseManager
from api.models.queryset.quality_issue_update_queryset import QualityIssueUpdateQueryset


class QualityIssueUpdateBaseManager(BaseManager):
    def get_queryset(self):
        self._queryset_class = QualityIssueUpdateQueryset
        return super().get_queryset()
