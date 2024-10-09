from typing import List

import pendulum
from django.db.models import QuerySet, Q

from api.http.filters import UserFilter
from api.services.csv_file_service import CsvFileService
from api.utilities.report_generators import BaseReportGenerator


class UserReportGenerator(BaseReportGenerator):

    def generatePdf(self):
        pass

    def generateCsv(self):
        titles = [
            'Status',
            'First Name',
            'Last Name',
            'Email',
            'Phone',
            'Position',
            'Company',
            'Role',
            'Projects',
            'Created Date',
        ]

        queryset = self.model.objects.only_active().select_related('company', 'group').prefetch_related('project_set')
        queryset = self.filter_queryset(queryset)
        queryset = self.search_in_queryset(queryset)

        rows_data = self.preparing_rows_data(queryset)
        file_name = f"Users_{pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')}.csv"
        csv_service = CsvFileService(file_name)
        return csv_service.create_file(titles, rows_data)

    def preparing_rows_data(self, queryset: QuerySet) -> List[List[str]]:
        date_format = '%d/%m/%Y'
        return [
            [user.get_status_display(),
             user.first_name,
             user.last_name,
             user.email,
             user.phone.as_e164,
             user.position,
             user.company.name if user.company_id else '',
             user.get_group_label(),
             self.get_projects(user.project_set.all()),
             user.created_at.strftime(date_format)]
            for user in queryset
        ]

    def get_projects(self, projects: QuerySet) -> str:
        return '\n'.join([project.name for project in projects])

    def search_in_queryset(self, queryset: QuerySet) -> QuerySet:
        search = self.request.query_params.get('search')
        if search:
            return queryset.filter(Q(first_name__icontains=search)
                                   | Q(email__icontains=search)
                                   | Q(last_name__icontains=search)
                                   | Q(company__name__icontains=search))
        return queryset

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        f = UserFilter(self.request.query_params, queryset=queryset)
        f.is_valid()
        return f.qs
