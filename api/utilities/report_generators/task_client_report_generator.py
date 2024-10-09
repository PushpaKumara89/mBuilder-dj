import csv
import re
import threading
import uuid
from io import StringIO, BytesIO
from queue import Queue

import pendulum
from PyPDF2 import PdfFileMerger, PdfFileReader
from azure.storage.blob import ContainerClient, BlobClient
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from wkhtmltopdf import render_pdf_from_template

from api.http.serializers import TasksReportSerializer
from api.storages import AzurePrivateReportStorage
from api.utilities.report_generators import BaseReportGenerator
from api.utilities.tasks_utilities import modify_queryset
from mbuild.settings import AZURE_BLOB_CONNECTION_STRING


class TaskClientReportGenerator(BaseReportGenerator):
    def generatePdf(self):
        from api.http.views import TaskViewSet

        def wait_threads():
            threads = []
            while not threads_batch.empty():
                threads.append(threads_batch.get())
            for thread in threads:
                thread.join()

        def sort_by_index(blob_file):
            return int(re.search(str(pdf_file_name_prefix) + r'_(\d+)\.pdf$', str(blob_file.name)).group(1))

        file_name = self._get_report_file_name() + '.pdf'
        pdf_file_name_prefix = f'task_client_report_temp_{uuid.uuid4()}'
        step = settings.PDF_FILE_GENERATION_CHUNK_SIZE
        start = 0
        end = step
        container_client = ContainerClient.from_connection_string(
            conn_str=AZURE_BLOB_CONNECTION_STRING,
            container_name=AzurePrivateReportStorage.azure_container
        )
        threads_batch = Queue(settings.PDF_FILE_GENERATION_THREADS_BATCH_SIZE)
        viewset = TaskViewSet()

        while True:
            queryset = self.model.all_objects

            for backend in list(viewset.filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, viewset)

            queryset = queryset.filter_by_project(self.request.parser_context['kwargs']) \
                .exclude_not_applicable() \
                .exclude_for_client_report()

            queryset = modify_queryset(queryset, self.request)
            tasks = queryset[start:end]

            if not tasks:
                break

            thread = threading.Thread(target=self.generate_file, args=(tasks, pdf_file_name_prefix, start))
            threads_batch.put(thread)
            thread.start()

            start += step
            end += step

            # Process threads by batch to avoid huge active threads amount.
            if threads_batch.full():
                wait_threads()

        if not threads_batch.empty():
            wait_threads()

        pdf_files_blobs = list(container_client.list_blobs(name_starts_with=str(pdf_file_name_prefix)))
        pdf_files_blobs = sorted(pdf_files_blobs, key=sort_by_index)
        merge_object = PdfFileMerger()
        for blob in pdf_files_blobs:
            stream = BytesIO()
            BlobClient.from_connection_string(
                conn_str=AZURE_BLOB_CONNECTION_STRING,
                container_name=AzurePrivateReportStorage.azure_container,
                blob_name=blob.name
            ).download_blob().readinto(stream)

            merge_object.append(PdfFileReader(stream), import_outline=False)

            BlobClient.from_connection_string(
                conn_str=AZURE_BLOB_CONNECTION_STRING,
                container_name=AzurePrivateReportStorage.azure_container,
                blob_name=blob.name
            ).delete_blob()

        final_pdf = BytesIO()
        merge_object.write(final_pdf)

        return SimpleUploadedFile(content=final_pdf.getvalue(), name=file_name, content_type='application/pdf')

    def generateCsv(self):
        from api.http.views import TaskViewSet

        file_name = self._get_report_file_name() + '.csv'
        f = StringIO()

        writer = csv.writer(f)
        writer.writerow([
            'Status', 'Quality Critical Task ID', 'Project Number',
            'Building', 'Level', 'Area', 'Package', 'Package Activity',
            'Quality Critical Task', 'Last Update Date', 'Last Update Time', 'Comments',
        ])

        queryset = self.model.all_objects
        viewset = TaskViewSet()

        for backend in list(viewset.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, viewset)

        queryset = queryset.filter_by_project(self.request.parser_context['kwargs']) \
            .exclude_not_applicable() \
            .exclude_for_client_report()

        queryset = modify_queryset(queryset, self.request).select_related(
            'location_matrix__project', 'package_activity', 'package_activity_task'
        )
        tasks_serializer = TasksReportSerializer(queryset,
                                                 expand=TasksReportSerializer.Meta.expandable_fields.keys(), many=True,
                                                 export_producer=TasksReportSerializer.ExportProducer.CSV)
        for task_data in tasks_serializer.data:
            writer.writerow([
                task_data['status'],
                task_data['expanded_quality_critical_task_id'],
                task_data['expanded_project_number'],

                task_data['expanded_building'],
                task_data['expanded_level'],
                task_data['expanded_area'],

                task_data['expanded_package'],
                task_data['expanded_package_activity_name'],
                task_data['expanded_package_activity_task_description'],

                task_data['expanded_last_update_date'],
                task_data['expanded_last_update_time'],
                task_data['expanded_comments'],
            ])

        return SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=file_name, content_type='text/csv')

    def _get_report_file_name(self):
        project_name = self.project.name.replace(' ', '_')
        current_date = pendulum.now().to_datetime_string().replace(' ', '_')

        return '%s-QCT-Report_Client_%s' % (project_name, current_date)

    def generate_file(self, tasks, pdf_file_name_prefix, start):
        tasks_serializer = TasksReportSerializer(
            tasks, many=True,
            expand=[key for key in TasksReportSerializer.Meta.expandable_fields.keys() if
                    key not in ['expanded_recipients']],
        )

        pdf = render_pdf_from_template(
            input_template='pdf/tasks_client_report.html',
            context={
                'project_number': self.project.number,
                'project_name': self.project.name,
                'tasks': tasks_serializer.data,
            },
            cmd_options={
                'margin-top': '0.1in',
                'margin-right': '0.1in',
                'margin-bottom': '0.1in',
                'margin-left': '0.1in',
                'orientation': 'landscape'
            },
            footer_template=None,
            header_template=None
        )

        BlobClient.from_connection_string(
            conn_str=AZURE_BLOB_CONNECTION_STRING,
            container_name=AzurePrivateReportStorage.azure_container,
            blob_name=f'{pdf_file_name_prefix}_{start}.pdf'
        ).upload_blob(pdf)