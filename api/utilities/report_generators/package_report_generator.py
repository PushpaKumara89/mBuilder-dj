from typing import List

import pendulum
from django.db.models import QuerySet

from api.services.csv_file_service import CsvFileService
from api.utilities.report_generators import BaseReportGenerator


class PackageReportGenerator(BaseReportGenerator):

    def generatePdf(self):
        pass

    def generateCsv(self):
        titles = [
            'Name',
            'Created Date',
        ]

        queryset = self.model.objects.order_by('order')

        rows_data = self.preparing_rows_data(queryset)
        file_name = f"Packages_{pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')}.csv"
        csv_service = CsvFileService(file_name)
        return csv_service.create_file(titles, rows_data)

    def preparing_rows_data(self, queryset: QuerySet) -> List[List[str]]:
        date_format = '%d/%m/%Y'
        return [
            [obj.name,
             obj.created_at.strftime(date_format)]
            for obj in queryset
        ]
