from django.db.models import QuerySet, OuterRef
from api.models.managers import BaseManager


class QualityIssueManager(BaseManager):
    def add_filters_for_floor_plan_subquery(self) -> QuerySet:
        return self.filter(
            location_matrix__project_id=OuterRef('project_id'),
            deleted__isnull=True,
            location_matrix__deleted__isnull=True,
            location_matrix__building=OuterRef('building'),
            location_matrix__level=OuterRef('level'),
        )

    def add_filters_for_floor_plan_area_pin_subquery(self, kwargs) -> QuerySet:
        return self.filter(
            id=OuterRef('object_id'),
            deleted__isnull=True,
            location_matrix__deleted__isnull=True,
            location_matrix__project=kwargs['project_pk'],
        )
