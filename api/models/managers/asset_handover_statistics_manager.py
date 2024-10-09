from django.db.models import F

from api.models.asset_handover import AssetHandoverDocumentMedia
from api.models.managers import BaseManager


class AssetHandoverStatisticsManager(BaseManager):
    def change_statistics_for_document_status(self, asset_handover_document_media: AssetHandoverDocumentMedia, multiplier: int) -> None:
        changing_field_name = '%s_count' % asset_handover_document_media.status
        asset_handover_document_id = int(asset_handover_document_media.asset_handover_document_id)
        filters = {'asset_handover_document_id': asset_handover_document_id}

        if multiplier > 0:
            filters.update(
                company__isnull=True,
                group__isnull=True,
            )
        elif multiplier < 0:
            filters[f'{changing_field_name}__gt'] = 0

        self.get_queryset().filter(**filters).update(**{changing_field_name: F(changing_field_name) + multiplier})

    def update_on_asset_handover_document_change(self, diff: int, asset_handover_document_id: int) -> None:
        self.get_queryset().filter(
            asset_handover_document_id=asset_handover_document_id,
        ).update(
            required_files_count=F('required_files_count') + diff
        )

    def update_on_asset_handover_document_media_status_change(self, document_media: AssetHandoverDocumentMedia) -> None:
        queryset = self.get_queryset().filter(
            asset_handover_document_id=document_media.asset_handover_document_id,
            company__isnull=True,
            group__isnull=True
        )

        if queryset.exists() and hasattr(document_media, 'update_fields_original_values'):
            old_status_count_field = '%s_count' % document_media.update_fields_original_values['status']
            new_status_count_field = '%s_count' % document_media.status

            queryset.update(**{
                old_status_count_field: F(old_status_count_field) - 1,
                new_status_count_field: F(new_status_count_field) + 1
            })
