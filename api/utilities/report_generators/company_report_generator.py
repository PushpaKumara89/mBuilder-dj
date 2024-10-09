from typing import List

import pendulum
from django.db.models import QuerySet, Count, Q

from api.http.filters.company.company_filter import CompanyFilter
from api.services.csv_file_service import CsvFileService
from api.utilities.report_generators import BaseReportGenerator


class CompanyReportGenerator(BaseReportGenerator):

    def generatePdf(self):
        pass

    def generateCsv(self):
        titles = [
            'Name',
            'Users',
            'Created Date',
        ]

        queryset = self.model.objects.annotate(user_count=Count('user', filter=Q(user__deleted__isnull=True)))
        queryset = self.filter_queryset(queryset)
        queryset = self.search_in_queryset(queryset)

        rows_data = self.preparing_rows_data(queryset)
        file_name = f"Companies_{pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')}.csv"
        csv_service = CsvFileService(file_name)
        return csv_service.create_file(titles, rows_data)

    def preparing_rows_data(self, queryset: QuerySet) -> List[List[str]]:
        date_format = '%d/%m/%Y'
        return [
            [obj.name,
             obj.user_count,
             obj.created_at.strftime(date_format)]
            for obj in queryset
        ]

    def search_in_queryset(self, queryset: QuerySet) -> QuerySet:
        search = self.request.query_params.get('search')
        if search:
            return queryset.filter(Q(name__icontains=search))
        return queryset

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        f = CompanyFilter(self.request.query_params, queryset=queryset)
        f.is_valid()
        return f.qs
