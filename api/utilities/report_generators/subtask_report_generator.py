import csv
from io import StringIO

import pendulum
from django.core.files.uploadedfile import SimpleUploadedFile
from wkhtmltopdf import render_pdf_from_template

from api.http.serializers.user import UserReportSerializer
from api.http.serializers.subtask.subtasks_report_serializer import SubtasksReportSerializer
from api.utilities.report_generators import BaseReportGenerator
from api.utilities.subtask_utilities import apply_common_filters_queryset, apply_default_ordering


class SubtaskReportGenerator(BaseReportGenerator):
    def generatePdf(self):
        from api.http.views import SubtaskViewSet

        file_name = self._get_report_file_name() + '.pdf'
        queryset = self.model.objects.all()
        viewset = SubtaskViewSet()
        queryset = apply_common_filters_queryset(queryset, self.request, self.request.parser_context['kwargs'])
        queryset = apply_default_ordering(queryset, self.request).select_related(
            'user__company', 'task__location_matrix__project', 'task__package_activity',
            'task__package_activity_task'
        )

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)

        subtasks_serializer = SubtasksReportSerializer(
            queryset,
            expand=[key for key in SubtasksReportSerializer.Meta.expandable_fields.keys()
                    if key not in ['expanded_recipients']],
            many=True
        )
        user_serializer = UserReportSerializer(
            self.request.user,
            expand=[key for key in UserReportSerializer.Meta.expandable_fields.keys()]
        )

        pdf = render_pdf_from_template(
            input_template='pdf/subtasks_report.html',
            context={
                'project_number': self.project.number,
                'project_name': self.project.name,
                'subtasks': subtasks_serializer.data,
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
        from api.http.views import SubtaskViewSet

        file_name = self._get_report_file_name() + '.csv'
        f = StringIO()

        writer = csv.writer(f)
        writer.writerow([
            'Rework ID', 'Rework Description', 'Project Number', 'Building', 'Level', 'Area', 'Location Description',
            'Package', 'Package Activity', 'Package Activity ID', 'Quality Critical Task', 'User Identified',
            'Date Raised', 'Time Raised', 'Attachment URLs', 'Date Complete', 'Time Complete', 'Recipients', 'Due Date',
            'Due Time', 'Estimated man hours to be completed', 'User Closed', 'Closed Comments', 'Closed Image URLs',
            'Status', 'Last User', 'Last Update Date', 'Last Update Time', 'Subcontractor Company',
            'Subcontractor Name', 'Latest Comment'
        ])

        queryset = self.model.objects.all()
        viewset = SubtaskViewSet()
        queryset = apply_common_filters_queryset(queryset, self.request, self.request.parser_context['kwargs'])
        queryset = apply_default_ordering(queryset, self.request)

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)

        subtasks_serializer = SubtasksReportSerializer(
            queryset,
            expand=SubtasksReportSerializer.Meta.expandable_fields.keys(),
            many=True,
            export_producer=SubtasksReportSerializer.ExportProducer.CSV
        )

        for subtask_data in subtasks_serializer.data:
            writer.writerow([
                self._get_rework_id(subtask_data),
                subtask_data['description'],
                subtask_data['expanded_project_number'],

                subtask_data['expanded_building'],
                subtask_data['expanded_level'],
                subtask_data['expanded_area'],
                subtask_data['location_description'],

                subtask_data['expanded_package'],
                subtask_data['expanded_package_activity_name'],
                subtask_data['expanded_package_activity_id'],
                subtask_data['expanded_package_activity_task_description'],

                subtask_data['expanded_identified_user'],
                subtask_data['expanded_date_raised'],
                subtask_data['expanded_time_raised'],
                subtask_data['expanded_files_urls'],

                subtask_data['expanded_date_of_completion'],
                subtask_data['expanded_time_of_completion'],

                subtask_data['expanded_recipients'],

                subtask_data['expanded_due_date'],
                subtask_data['expanded_due_time'],

                subtask_data['expanded_estimation'],

                subtask_data['expanded_user_closed'],
                subtask_data['expanded_closed_comments'],
                subtask_data['expanded_closed_files_urls'],

                subtask_data['expanded_last_status'],
                subtask_data['expanded_last_user'],
                subtask_data['expanded_last_update_date'],
                subtask_data['expanded_last_update_time'],

                subtask_data['subcontractor_company'],
                subtask_data['subcontractor_name'],
                subtask_data['expanded_last_comment'],
            ])

        return SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=file_name, content_type='text/csv')

    def _get_report_file_name(self):
        project_name = self.project.name.replace(' ', '-')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')

        return '%s-R-Report_%s' % (project_name, current_date)

    def _get_rework_id(self, task_data):
        return '%s-R-%s%s' % (task_data['expanded_project_number'], task_data['id'],
                              f" (QI-{task_data['quality_issue']})" if task_data['quality_issue'] else '')
