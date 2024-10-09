import csv
from io import StringIO

import pendulum

from api.models import PackageHandoverDocumentMedia, AssetHandoverDocumentMedia, Project


class HandoverDocumentArchiveReportGenerator:
    def __init__(self, project: Project):
        self.project = project

    def generate_csv(self) -> tuple:
        file_name = self._get_report_file_name() + '.csv'
        f = StringIO()
        writer = csv.writer(f)
        writer.writerow([
            'Building',
            'Level',
            'Area',
            'Package',
            'Package Activity',
            'Company',
            'Document Type',
            'File Name',
            'UID',
            'Information',
            'File Type'
        ])

        self.__add_package_handover_rows(writer)
        self.__add_asset_handover_rows(writer)

        return f.getvalue(), file_name

    def __add_package_handover_rows(self, writer) -> None:
        from api.http.serializers.package_handover.package_handover_document_media import \
            PackageHandoverDocumentMediaReportSerializer

        queryset = PackageHandoverDocumentMedia.objects.filter(
            package_handover_document__project=self.project,
            package_handover_document__package_handover__deleted__isnull=True,
        ).all()

        package_handover_document_media_serializer = PackageHandoverDocumentMediaReportSerializer(
            queryset,
            many=True,
            expand=[
                'expanded_company',
                'expanded_extension',
                'expanded_title',
            ],
            export_producer=PackageHandoverDocumentMediaReportSerializer.ExportProducer.CSV
        )

        for package_handover_document_media in package_handover_document_media_serializer.data:
            writer.writerow([
                '',
                '',
                '',
                package_handover_document_media['package'],
                package_handover_document_media['package_activity'],
                package_handover_document_media['expanded_company'],
                package_handover_document_media['package_handover_document_type'],
                package_handover_document_media['expanded_title'],
                package_handover_document_media['uid'],
                package_handover_document_media['information'],
                package_handover_document_media['expanded_extension'],
            ])

    def __add_asset_handover_rows(self, writer) -> None:
        from api.http.serializers.asset_handover.asset_handover_document_media.asset_handover_document_media_report_serializer import \
            AssetHandoverDocumentMediaReportSerializer

        queryset = AssetHandoverDocumentMedia.objects.filter(
            asset_handover_document__asset_handover__project=self.project,
            asset_handover_document__asset_handover__deleted__isnull=True,
            asset_handover_document__deleted__isnull=True,
        ).all()

        asset_handover_document_media_serializer = AssetHandoverDocumentMediaReportSerializer(
            queryset,
            many=True,
            expand=[
                'expanded_building',
                'expanded_level',
                'expanded_area',
                'expanded_package',
                'expanded_company',
                'expanded_extension',
            ],
            export_producer=AssetHandoverDocumentMediaReportSerializer.ExportProducer.CSV
        )

        for asset_handover_document_media in asset_handover_document_media_serializer.data:
            writer.writerow([
                asset_handover_document_media['expanded_building'],
                asset_handover_document_media['expanded_level'],
                asset_handover_document_media['expanded_area'],
                asset_handover_document_media['expanded_package'],
                asset_handover_document_media['package_activity'],
                asset_handover_document_media['expanded_company'],
                asset_handover_document_media['asset_handover_document_type'],
                asset_handover_document_media['title'],
                asset_handover_document_media['uid'],
                '',
                asset_handover_document_media['expanded_extension'],
            ])

    def _get_report_file_name(self):
        project_name = self.project.name.replace(' ', '_')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_')

        return '%s_Handover-Document_%s' % (project_name, current_date)
