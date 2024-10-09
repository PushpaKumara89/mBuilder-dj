import csv
from io import StringIO

import pendulum
from django.core.files.uploadedfile import SimpleUploadedFile

from api.http.serializers.package_handover.package_handover_document_media import PackageHandoverDocumentMediaReportSerializer
from api.models import PackageHandover
from api.utilities.report_generators import BaseReportGenerator


class PackageHandoverDocumentMediaReportGenerator(BaseReportGenerator):
    def generateCsv(self):
        from api.http.views import PackageHandoverViewSet

        file_name = self._get_report_file_name() + '.csv'

        viewset = PackageHandoverViewSet()
        queryset = PackageHandover.objects.filter(
            package_matrix__project=self.request.parser_context['kwargs']['project_pk']
        ).all()

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)

        queryset = self.model.objects.filter(
            package_handover_document__package_handover__deleted__isnull=True,
            package_handover_document__package_handover__in=list(queryset.values_list('id', flat=True))
        )

        f = StringIO()

        writer = csv.writer(f)
        writer.writerow([
            'Status',
            'Document UID',
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

        package_handover_document_media_serializer = PackageHandoverDocumentMediaReportSerializer(
            queryset,
            many=True,
            expand=PackageHandoverDocumentMediaReportSerializer.Meta.expandable_fields.keys(),
            export_producer=PackageHandoverDocumentMediaReportSerializer.ExportProducer.CSV
        )

        for package_handover_document_media in package_handover_document_media_serializer.data:
            writer.writerow([
                package_handover_document_media['expanded_status_view'],
                package_handover_document_media['uid'],
                package_handover_document_media['package'],
                package_handover_document_media['package_activity'],
                package_handover_document_media['package_activity_id'],
                package_handover_document_media['expanded_user_identified'],
                package_handover_document_media['expanded_last_uploaded_date'],
                package_handover_document_media['expanded_last_uploaded_time'],
                package_handover_document_media['expanded_last_modified_date'],
                package_handover_document_media['expanded_last_modified_time'],
                package_handover_document_media['expanded_completed_date'],
                package_handover_document_media['expanded_completed_time'],
                package_handover_document_media['expanded_status_history'],
                package_handover_document_media['expanded_status_by'],
                package_handover_document_media['expanded_status_comments'],
                package_handover_document_media['expanded_status_change_date'],
                package_handover_document_media['expanded_status_change_time'],
                package_handover_document_media['expanded_title'],
                package_handover_document_media['package_handover_document_type'],
                package_handover_document_media['expanded_extension'],
            ])

        return SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=file_name, content_type='text/csv')

    def generatePdf(self):
        pass

    def _get_report_file_name(self):
        project_name = self.project.name.replace(' ', '_')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_')

        return '%s_Package_Handover_Report_%s' % (project_name, current_date)
