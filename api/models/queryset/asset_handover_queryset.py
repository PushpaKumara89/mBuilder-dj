from django.db.models import Count, Q

from api.models.queryset import SafeDeleteQueryset


class AssetHandoverQueryset(SafeDeleteQueryset):
    def get_information_statistics(self):
        return self.aggregate(
            filled_information_count=Count('assethandoverinformation', filter=Q(
                Q(assethandoverinformation__guid_external_ref__isnull=False) & ~Q(assethandoverinformation__guid_external_ref=''),
                Q(assethandoverinformation__warranty__isnull=False) & ~Q(assethandoverinformation__warranty=''),
                Q(assethandoverinformation__manufacture_serial_number__isnull=False) & ~Q(assethandoverinformation__manufacture_serial_number=''),
                Q(assethandoverinformation__model_number__isnull=False) & ~Q(assethandoverinformation__model_number=''),
                assethandoverdocument__deleted__isnull=True
            )),
            total_information_count=Count('assethandoverinformation')
        )

    def get_for_project_package_activity(self, project_id: int, package_activity_id: int):
        return self.prefetch_related('assethandoverdocument_set').filter(
            location_matrix__project_id=project_id,
            location_matrix__locationmatrixpackage__enabled=True,
            location_matrix__locationmatrixpackage__package_activity_id=package_activity_id,
            package_activity_id=package_activity_id
        ).all()
