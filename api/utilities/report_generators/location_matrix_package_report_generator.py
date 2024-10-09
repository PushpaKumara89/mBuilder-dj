from typing import List

import pendulum
from django.db.models import QuerySet, Subquery

from api.http.filters.location_matrix_package_filter import LocationMatrixPackageFilter
from api.services.csv_file_service import CsvFileService
from api.utilities.location_matrix_utilities import annotate_location_matrix_level_parts
from api.utilities.report_generators import BaseReportGenerator


class LocationMatrixPackageReportGenerator(BaseReportGenerator):

    def generatePdf(self):
        pass

    def generateCsv(self):
        main_titles = [
            'Package',
            'Building',
            'Level',
            'Area',
        ]

        queryset = self.model.objects.filter(
            location_matrix__project=self.project,
            location_matrix__deleted__isnull=True
        ).select_related(
            'location_matrix',
            'package_matrix',
            'package',
            'package_activity'
        )

        queryset = self.filter_queryset(queryset)
        package_activities = self.get_package_activities(queryset)
        titles = self.get_titles(package_activities, main_titles)
        rows_data = self.preparing_rows_data(queryset, package_activities)
        file_name = f"Location_Matrix_Package_{pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')}.csv"
        csv_service = CsvFileService(file_name)

        return csv_service.create_file(titles, rows_data)

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        f = LocationMatrixPackageFilter(self.request.query_params, queryset=queryset)
        f.is_valid()

        return f.qs

    def get_package_activities(self, queryset: QuerySet) -> List:
        package_activities = list(queryset.values('package_activity_id', 'package_activity__name')
                                          .distinct('package_activity_id')
                                          .order_by('package_activity_id'))
        package_activities.sort(key=lambda key: key['package_activity__name'])

        return package_activities

    def get_titles(self, package_activities: List, main_titles: List) -> List[str]:
        return main_titles + [package_activity['package_activity__name'] for package_activity in package_activities]

    def preparing_rows_data(self, queryset: QuerySet, package_activities) -> List[List[str]]:
        matrix = {(obj.package_id, obj.location_matrix_id, obj.package_activity_id,): obj for obj in queryset}
        queryset = annotate_location_matrix_level_parts(queryset, level_field='location_matrix__level')
        rows = list(
            queryset.filter(id__in=Subquery(
                (
                    queryset
                    .distinct('package_id', 'location_matrix_id')
                    .order_by('package_id', 'location_matrix_id')
                    .values('id')
                )
            )).order_by('package__order', 'location_matrix__building', '-level_number',
                        'level_postfix', 'location_matrix__area')
        )

        data = []
        for row in rows:
            first_row_records = [row.package.name, row.location_matrix.building, row.location_matrix.level, row.location_matrix.area]
            last_row_records = [self.boll_to_human_case(self.get_obj_matrix((row.package_id, row.location_matrix_id, package_activity['package_activity_id'],),
                                                                            matrix))
                                for package_activity in package_activities]
            row_records = first_row_records + last_row_records
            data.append(row_records)

        return data

    def get_obj_matrix(self, key: tuple, matrix: dict) -> bool:
        try:
            return matrix[key].enabled
        except KeyError:
            return False

    def boll_to_human_case(self, value: bool) -> str:
        return 'Yes' if value else ''
