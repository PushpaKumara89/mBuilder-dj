from django.db.models import QuerySet, OuterRef
from api.models.managers import BaseManager


class SubtaskManager(BaseManager):
    def add_filters_for_floor_plan_subquery(self) -> QuerySet:
        return self.filter(
            deleted__isnull=True,
            task__deleted__isnull=True,
            task__package_activity__deleted__isnull=True,
            task__package_activity__packagematrix__deleted__isnull=True,
            task__package_activity__packagematrix__project_id=OuterRef('project_id'),
            task__package_activity__packagematrix__package=OuterRef('package_id'),
        )

    def add_filters_for_floor_plan_area_pin_subquery(self, kwargs) -> QuerySet:
        return self.get_queryset().filter(
            id=OuterRef('object_id'),
            deleted__isnull=True,
            task__deleted__isnull=True,
            task__package_activity__deleted__isnull=True,
            task__package_activity__packagematrix__deleted__isnull=True,
            task__package_activity__packagematrix__project=kwargs['project_pk'],
        )
