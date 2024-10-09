from api.models.queryset import SafeDeleteQueryset


class AssetHandoverDocumentMediaQueryset(SafeDeleteQueryset):
    def filter_for_handover_document_archive(self, project):
        return self.filter(
            asset_handover_document__asset_handover__project=project,
            asset_handover_document__deleted__isnull=True,
            asset_handover_document__asset_handover__deleted__isnull=True,
            asset_handover_document__asset_handover__location_matrix__deleted__isnull=True,
            status__in=[
                self.model.Status.REQUESTING_APPROVAL,
                self.model.Status.ACCEPTED
            ]
        )
