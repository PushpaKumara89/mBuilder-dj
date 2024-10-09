import csv
from io import StringIO

import pendulum
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q

from api.http.serializers.handover_document_serializer import HandoverDocumentSerializer
from api.models import AssetHandoverDocumentType, PackageHandoverDocumentType
from api.utilities.handover_document_utilities import add_filters_by_user_role, add_document_type_filters, \
    add_filters_by_locations
from api.utilities.report_generators import BaseReportGenerator


class HandoverDocumentReportGenerator(BaseReportGenerator):
    def generatePdf(self):
        pass

    def generateCsv(self):
        from api.http.views.handover_document.handover_document_view_set import HandoverDocumentViewSet

        file_name = self.__get_report_file_name() + '.csv'
        f = StringIO()

        writer = csv.writer(f)
        writer.writerow([
            'Building', 'Level', 'Area', 'Package', 'Package Activity', 'Company',
            'Document Type', 'File Name', 'UID', 'Information', 'File Type',
        ])

        queryset = self.model.objects.all()
        viewset = HandoverDocumentViewSet()
        handover_documents_filters = [Q(project=self.project)]

        add_filters_by_user_role(self.request.user, handover_documents_filters, self.project.pk)
        add_document_type_filters(self.request, handover_documents_filters)
        add_filters_by_locations(self.request, handover_documents_filters, self.project.pk)

        queryset = queryset.filter(*handover_documents_filters)

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)

        queryset = queryset.select_related(
            'package', 'package_activity', 'company', 'media'
        )

        context = {
            'asset_handover_document_types': AssetHandoverDocumentType.objects.all(),
            'package_handover_document_types': PackageHandoverDocumentType.objects.all()
        }
        handover_document_serializer = HandoverDocumentSerializer(
            queryset,
            expand=HandoverDocumentSerializer.Meta.expandable_fields.keys(),
            many=True,
            context=context
        )

        for handover_document in handover_document_serializer.data:
            writer.writerow([
                handover_document['building'],
                handover_document['level'],
                handover_document['area'],
                handover_document['expanded_package']['name'],
                handover_document['expanded_package_activity']['name'],
                handover_document['expanded_company']['name'],
                handover_document['expanded_document_type']['name'],
                handover_document['filename'],
                handover_document['uid'],
                handover_document['information'],
                handover_document['file_type'],
            ])

        return SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=file_name, content_type='text/csv')

    def __get_report_file_name(self):
        project_name = self.project.name.replace(' ', '-')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')

        return '%s-Handover_Document_%s' % (project_name, current_date)
