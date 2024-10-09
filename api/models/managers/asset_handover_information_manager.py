from django.db.models import Count, Q

from api.models.managers import BaseManager


class AssetHandoverInformationManager(BaseManager):
    def aggregate_statistics_by_project(self, project) -> dict:
        return self.get_queryset().filter(asset_handover__project=project).aggregate(
            total_information_count=Count('id'),
            filled_information_count=Count('id', filter=Q(
                Q(guid_external_ref__isnull=False) & ~Q(guid_external_ref=''),
                Q(warranty__isnull=False) & ~Q(warranty=''),
                Q(manufacture_serial_number__isnull=False) & ~Q(manufacture_serial_number=''),
                Q(model_number__isnull=False) & ~Q(model_number=''),
            ))
        )
