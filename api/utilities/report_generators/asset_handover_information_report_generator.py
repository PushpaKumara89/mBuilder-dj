import csv
from io import StringIO

import pendulum
from django.core.files.uploadedfile import SimpleUploadedFile

from api.http.serializers.asset_handover.asset_handover_document_media.asset_handover_document_media_report_serializer import \
    AssetHandoverDocumentMediaReportSerializer
from api.models import AssetHandoverDocumentMedia
from api.utilities.report_generators import BaseReportGenerator


class AssetHandoverInformationReportGenerator(BaseReportGenerator):
    def generateCsv(self):
        from api.http.views import AssetHandoverDocumentMediaViewSet

        file_name = self._get_report_file_name() + '.csv'

        viewset = AssetHandoverDocumentMediaViewSet()
        queryset = AssetHandoverDocumentMedia.objects.filter(
            asset_handover_document__asset_handover__project=self.request.parser_context['kwargs']['project_pk'],
            asset_handover_document__asset_handover__deleted__isnull=True,
            asset_handover_document__deleted__isnull=True,
        ).all()

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)

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

        return SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=file_name, content_type='text/csv')

    def generatePdf(self):
        pass

    def _get_report_file_name(self):
        project_name = self.project.name.replace(' ', '_')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_')

        return '%s_Handover_Information_Report_%s' % (project_name, current_date)
