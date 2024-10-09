from typing import List

import pendulum
from django.db.models import QuerySet

from api.http.filters import LocationMatrixFilter
from api.services.csv_file_service import CsvFileService
from api.utilities.location_matrix_utilities import annotate_location_matrix_level_parts
from api.utilities.report_generators import BaseReportGenerator


class LocationMatrixReportGenerator(BaseReportGenerator):

    def generatePdf(self):
        pass

    def generateCsv(self):
        titles = [
            'Building',
            'Level',
            'Area',
        ]

        queryset = annotate_location_matrix_level_parts(self.model.objects)
        queryset = queryset.filter(project=self.project).order_by('building', '-level_number', 'level_postfix', 'area').all()
        queryset = self.filter_queryset(queryset).distinct()

        rows_data = self.preparing_rows_data(queryset)
        file_name = f"Location_Matrix_{pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')}.csv"
        csv_service = CsvFileService(file_name)

        return csv_service.create_file(titles, rows_data)

    def preparing_rows_data(self, queryset: QuerySet) -> List[List[str]]:
        return [
            [obj.building, obj.level, obj.area]
            for obj in queryset
        ]

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        f = LocationMatrixFilter(self.request.query_params, queryset=queryset)
        f.is_valid()

        return f.qs
