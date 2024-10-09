import csv
from io import StringIO

import pendulum
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Prefetch
from wkhtmltopdf import render_pdf_from_template

from api.http.serializers.user import UserReportSerializer
from api.http.serializers.quality_issue.quality_issue_report_serializer import QualityIssueReportSerializer
from api.models import QualityIssueUpdate
from api.utilities.quality_issue_utilities import apply_default_queryset_filters
from api.utilities.report_generators import BaseReportGenerator


class QualityIssueReportGenerator(BaseReportGenerator):
    def generatePdf(self):
        from api.http.views import QualityIssueViewSet

        file_name = self.__get_report_file_name() + '.pdf'
        queryset = self.model.objects.all()
        viewset = QualityIssueViewSet()
        queryset = apply_default_queryset_filters(self.request.parser_context['kwargs'], queryset, self.request)

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)
        queryset = queryset.select_related(
            'location_matrix__project', 'user__company', 'response_category'
        )
        quality_issue_serializer = QualityIssueReportSerializer(
            queryset,
            expand=QualityIssueReportSerializer.Meta.expandable_fields.keys(),
            many=True
        )

        user_serializer = UserReportSerializer(
            self.request.user,
            expand=[key for key in UserReportSerializer.Meta.expandable_fields.keys()]
        )

        pdf = render_pdf_from_template(
            input_template='pdf/quality_issue_report.html',
            context={
                'project_number': self.project.number,
                'project_name': self.project.name,
                'quality_issues': quality_issue_serializer.data,
                'user': user_serializer.data,
                'created_at': pendulum.now()
            },
            cmd_options={
                'margin-top': '0in',
                'margin-right': '0in',
                'margin-bottom': '0in',
                'margin-left': '0in',
                'orientation': 'landscape'
            },
            footer_template=None,
            header_template=None
        )

        return SimpleUploadedFile(content=pdf, name=file_name, content_type='application/pdf')

    def generateCsv(self):
        from api.http.views import QualityIssueViewSet

        file_name = self.__get_report_file_name() + '.csv'
        f = StringIO()

        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Building', 'Level', 'Area', 'Quality Issue Description', 'Attachments URLs', 'Status By',
            'Created By', 'Created Date', 'Created Time', 'Response category', 'Response Date', 'Response Time',
            'Current Status', 'Latest Comment', 'Comment User', 'Comment Date'
        ])

        queryset = self.model.objects.all()
        viewset = QualityIssueViewSet()
        queryset = apply_default_queryset_filters(self.request.parser_context['kwargs'], queryset, self.request)

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)

        queryset = queryset.select_related(
            'location_matrix__project',
            'user__company',
            'response_category'
        ).prefetch_related(
            'attachments',
            Prefetch(
                'qualityissueupdate_set',
                queryset=QualityIssueUpdate.objects.filter(
                    is_comment=True).select_related('user').order_by('-created_at'),
                to_attr='latest_comment'
            )
        )

        quality_issue_serializer = QualityIssueReportSerializer(
            queryset,
            expand=QualityIssueReportSerializer.Meta.expandable_fields.keys(),
            many=True,
            export_producer=QualityIssueReportSerializer.ExportProducer.CSV
        )

        for quality_issue_data in quality_issue_serializer.data:
            writer.writerow([
                quality_issue_data['expanded_id'],
                quality_issue_data['expanded_building'],
                quality_issue_data['expanded_level'],
                quality_issue_data['expanded_area'],
                quality_issue_data['description'],
                quality_issue_data['expanded_files_urls'],
                quality_issue_data['expanded_status_by'],
                quality_issue_data['expanded_created_by'],
                quality_issue_data['expanded_created_date'],
                quality_issue_data['expanded_created_time'],
                quality_issue_data['expanded_response_category'],
                quality_issue_data['expanded_response_date'],
                quality_issue_data['expanded_response_time'],
                quality_issue_data['expanded_status_name'],
                quality_issue_data['expanded_latest_comment'],
                quality_issue_data['expanded_latest_comment_user'],
                quality_issue_data['expanded_latest_comment_date']
            ])

        return SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=file_name, content_type='text/csv')

    def __get_report_file_name(self):
        project_name = self.project.name.replace(' ', '-')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')

        return '%s-QI-Report_%s' % (project_name, current_date)
