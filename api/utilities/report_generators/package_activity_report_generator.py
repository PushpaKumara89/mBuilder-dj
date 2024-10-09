from typing import List

import pendulum
from django.db.models import QuerySet, Q

from api.http.filters.package_activity import PackageActivityFilter
from api.models import Project
from api.services.csv_file_service import CsvFileService
from api.utilities.report_generators import BaseReportGenerator


class PackageActivityReportGenerator(BaseReportGenerator):

    def generatePdf(self):
        pass

    def generateCsv(self):
        titles = [
            'Name',
            'Activity ID',
            'Quality Critical Tasks',
            'Projects',
            'Files',
        ]

        queryset = self.model.objects.prefetch_related('files', 'packageactivitytask_set')
        queryset = self.filter_queryset(queryset)
        queryset = self.search_in_queryset(queryset)

        rows_data = self.preparing_rows_data(queryset)
        file_name = f"Package_Activities_{pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')}.csv"
        csv_service = CsvFileService(file_name)
        return csv_service.create_file(titles, rows_data)

    def preparing_rows_data(self, queryset: QuerySet) -> List[List[str]]:
        return [
            [obj.name,
             obj.activity_id or '',
             self.get_quality_critical_tasks(obj.packageactivitytask_set.all()),
             self.get_projects_names(obj.id),
             self.get_files_urls(obj.files.all())]
            for obj in queryset
        ]

    def get_projects_names(self, activity_pk: int) -> str:
        queryset = Project.objects.filter(
            packagematrix__deleted__isnull=True,
            packagematrix__package__deleted__isnull=True,
            packagematrix__package_activity__pk=activity_pk,
            deleted__isnull=True
        )
        return '\n'.join([project.name for project in queryset])

    def search_in_queryset(self, queryset: QuerySet) -> QuerySet:
        search = self.request.query_params.get('search')
        if search:
            return queryset.filter(Q(name__icontains=search))
        return queryset

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        f = PackageActivityFilter(self.request.query_params, queryset=queryset)
        f.is_valid()
        return f.qs

    def get_files_urls(self, files: QuerySet) -> str:
        return '\n'.join([file.get_full_link() for file in files])

    def get_quality_critical_tasks(self, tasks: QuerySet) -> str:
        return '\n'.join([f'{i}. {task.description}' for i, task in enumerate(tasks, start=1)])
