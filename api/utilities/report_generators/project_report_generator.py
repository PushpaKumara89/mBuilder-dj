from typing import List

import pendulum
from django.db.models import QuerySet, Q

from api.http.filters.project_filter import ProjectFilter
from api.services.csv_file_service import CsvFileService
from api.utilities.report_generators import BaseReportGenerator


class ProjectReportGenerator(BaseReportGenerator):

    def generatePdf(self):
        pass

    def generateCsv(self):
        titles = [
            'Name',
            'Project number',
            'Image URL',
            'Status',
            'Created Date',
            'Start date',
            'PC date',
            'Project value',
            'Show estimated man hours',
            'Show rework and defects for clients',
            'Show quality report for clients',
        ]

        queryset = self.model.objects.select_related('image')

        queryset = self.filter_queryset(queryset)
        queryset = self.search_in_queryset(queryset)

        rows_data = self.preparing_rows_data(queryset)
        file_name = f"Projects_{pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')}.csv"
        csv_service = CsvFileService(file_name)
        return csv_service.create_file(titles, rows_data)

    def preparing_rows_data(self, queryset: QuerySet) -> List[List[str]]:
        date_format = '%d/%m/%Y'
        return [
            [obj.name,
             obj.number,
             obj.image.get_full_link() if getattr(obj, 'image', None) else '',
             obj.get_status_display(),
             obj.created_at.strftime(date_format),
             obj.start_date.strftime(date_format),
             obj.completion_date.strftime(date_format),
             obj.value if obj.value else 0,
             self.boll_to_human_case(obj.show_estimated_man_hours),
             self.boll_to_human_case(obj.is_subtask_visible_for_clients),
             self.boll_to_human_case(obj.is_task_visible_for_clients)]
            for obj in queryset
        ]

    def search_in_queryset(self, queryset: QuerySet) -> QuerySet:
        search = self.request.query_params.get('search')
        if search:
            return queryset.filter(Q(name__icontains=search) | Q(number__icontains=search))
        return queryset

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        f = ProjectFilter(self.request.query_params, queryset=queryset)
        f.is_valid()
        return f.qs

    def boll_to_human_case(self, value: bool) -> str:
        return 'Yes' if value else 'No'

