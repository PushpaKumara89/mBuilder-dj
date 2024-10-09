from django.db.models import Prefetch, QuerySet

from api.models.queryset import SafeDeleteQueryset


class PackageQueryset(SafeDeleteQueryset):
    def get_expanded_projects_count(self) -> QuerySet:
        from api.models import PackageMatrix
        return self.prefetch_related(
            Prefetch('packagematrix_set',
                     queryset=PackageMatrix.objects.filter(
                         deleted__isnull=True,
                         package_activity__deleted__isnull=True,
                         project__deleted__isnull=True
                     ).order_by('project_id', 'package_id').distinct('project_id', 'package_id'),
                     to_attr='not_deleted_packagematrix_set')
        )

    def projects_count(self, package_pk: int) -> int:
        return self.filter(
            packagematrix__deleted__isnull=True,
            packagematrix__package_activity__deleted__isnull=True,
            packagematrix__package__pk=package_pk,
            deleted__isnull=True
        ).distinct().count()
