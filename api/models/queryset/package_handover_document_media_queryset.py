from api.models.queryset import SafeDeleteQueryset


class PackageHandoverDocumentMediaQueryset(SafeDeleteQueryset):
    def filter_for_handover_document_archive(self, project):
        return self.filter(
            package_handover_document__project=project,
            package_handover_document__deleted__isnull=True,
            package_handover_document__package_handover__deleted__isnull=True,
            package_handover_document__package_handover__package_matrix__deleted__isnull=True,
            status__in=[
                self.model.Status.REQUESTING_APPROVAL,
                self.model.Status.ACCEPTED
            ]
        )
