import csv
from io import StringIO

import pendulum
from django.core.files.uploadedfile import SimpleUploadedFile

from api.http.serializers.asset_handover.asset_handover_document_media.asset_handover_document_media_report_serializer import \
    AssetHandoverDocumentMediaReportSerializer
from api.models import AssetHandover
from api.utilities.report_generators import BaseReportGenerator


class AssetHandoverDocumentMediaReportGenerator(BaseReportGenerator):
    def generateCsv(self):
        from api.http.views import AssetHandoverViewSet

        file_name = self._get_report_file_name() + '.csv'

        viewset = AssetHandoverViewSet()
        queryset = AssetHandover.objects.filter(
            location_matrix__project=self.request.parser_context['kwargs']['project_pk']
        ).all()

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)

        queryset = self.model.objects.select_related('asset_handover_document__asset_handover__location_matrix').filter(
            asset_handover_document__asset_handover__deleted__isnull=True,
            asset_handover_document__asset_handover__in=queryset.values('id')
        )

        f = StringIO()

        writer = csv.writer(f)
        writer.writerow([
            'Status',
            'Document UID',
            'Building',
            'Level',
            'Area',
            'Package',
            'Package Activity',
            'Package Activity ID',
            'User Identified',
            'Date Uploaded',
            'Time Uploaded',
            'Date Modified',
            'Time Modified',
            'Date Complete',
            'Time Complete',
            'Status History',
            'Status By',
            'Status Comments',
            'Status Change Date',
            'Status Change Time',
            'Document Title',
            'Document Type',
            'Document Format',
        ])
        queryset = queryset.select_related(
            'asset_handover_document__asset_handover__location_matrix', 'media'
        )
        asset_handover_document_media_serializer = AssetHandoverDocumentMediaReportSerializer(
            queryset,
            many=True,
            expand=AssetHandoverDocumentMediaReportSerializer.Meta.expandable_fields.keys(),
            export_producer=AssetHandoverDocumentMediaReportSerializer.ExportProducer.CSV
        )

        for asset_handover_document_media in asset_handover_document_media_serializer.data:
            writer.writerow([
                asset_handover_document_media['expanded_status_view'],
                asset_handover_document_media['uid'],

                asset_handover_document_media['expanded_building'],
                asset_handover_document_media['expanded_level'],
                asset_handover_document_media['expanded_area'],

                asset_handover_document_media['expanded_package'],
                asset_handover_document_media['package_activity'],
                asset_handover_document_media['package_activity_id'],

                asset_handover_document_media['expanded_user_identified'],
                asset_handover_document_media['expanded_last_uploaded_date'],
                asset_handover_document_media['expanded_last_uploaded_time'],
                asset_handover_document_media['expanded_last_modified_date'],
                asset_handover_document_media['expanded_last_modified_time'],
                asset_handover_document_media['expanded_completed_date'],
                asset_handover_document_media['expanded_completed_time'],

                asset_handover_document_media['expanded_status_history'],
                asset_handover_document_media['expanded_status_by'],
                asset_handover_document_media['expanded_status_comments'],
                asset_handover_document_media['expanded_status_change_date'],
                asset_handover_document_media['expanded_status_change_time'],

                asset_handover_document_media['title'],
                asset_handover_document_media['asset_handover_document_type'],
                asset_handover_document_media['expanded_extension'],
            ])

        return SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=file_name, content_type='text/csv')

    def generatePdf(self):
        pass

    def _get_report_file_name(self):
        project_name = self.project.name.replace(' ', '_')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_')

        return '%s_Asset_Handover_Report_%s' % (project_name, current_date)
