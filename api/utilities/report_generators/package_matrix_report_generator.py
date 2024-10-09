from collections import OrderedDict
from typing import List

import pendulum

from api.services.csv_file_service import CsvFileService
from api.utilities.report_generators import BaseReportGenerator


class PackageMatrixGenerator(BaseReportGenerator):

    def generatePdf(self):
        pass

    def generateCsv(self):
        packages = list(self.model.objects
                        .filter(project=self.project)
                        .values('package_id', 'package__name', 'package__order')
                        .distinct('package_id')
                        .order_by('package_id'))

        packages.sort(key=lambda key: key['package__order'])

        titles = [package['package__name'] for package in packages]

        rows_data = self.preparing_rows_data(packages)
        file_name = f"Package_Matrix_{pendulum.now().to_datetime_string().replace(' ', '_').replace(':', '-')}.csv"
        csv_service = CsvFileService(file_name)
        return csv_service.create_file(titles, rows_data)

    def preparing_rows_data(self, packages) -> List[List[str]]:
        package_activities = {}
        for package_matrix in self.model.objects.filter(project=self.project).select_related('package_activity').order_by('-package_activity__name'):
            package_id = str(package_matrix.package_id)
            if package_id in package_activities:
                package_activities[package_id].append(package_matrix.package_activity.name)
            else:
                package_activities[package_id] = [package_matrix.package_activity.name]

        try:
            count_package_activity_name = len(max(package_activities.values(), key=lambda key: len(key)))
        except ValueError:
            return []

        return [
            [package_activities.get(str(package['package_id']), []).pop() if package_activities.get(str(package['package_id']), []) else ''
             for package in packages]
            for _ in range(count_package_activity_name)
        ]
