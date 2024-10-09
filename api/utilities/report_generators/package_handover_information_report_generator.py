import csv
from io import StringIO

import pendulum
from django.core.files.uploadedfile import SimpleUploadedFile

from api.http.serializers.package_handover.package_handover_document_media import PackageHandoverDocumentMediaReportSerializer
from api.models import PackageHandover, PackageHandoverDocumentMedia
from api.utilities.report_generators import BaseReportGenerator


class PackageHandoverInformationReportGenerator(BaseReportGenerator):
    def generateCsv(self):
        from api.http.views import PackageHandoverDocumentMediaViewSet

        file_name = self._get_report_file_name() + '.csv'

        viewset = PackageHandoverDocumentMediaViewSet()
        queryset = PackageHandoverDocumentMedia.objects.filter(
            package_handover_document__project=self.request.parser_context['kwargs']['project_pk'],
            package_handover_document__package_handover__deleted__isnull=True,
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

        return SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=file_name, content_type='text/csv')

    def generatePdf(self):
        pass

    def _get_report_file_name(self):
        project_name = self.project.name.replace(' ', '_')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_')

        return '%s_Handover_Information_Report_%s' % (project_name, current_date)
