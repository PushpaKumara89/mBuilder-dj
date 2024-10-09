from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Update location matrix package's package matrix."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("""
                with t as (select lmp.id                  lmp_id,
                                  pm1.id                  pm_id,
                                  pm1.package_id          pm_package_id,
                                  pm1.package_activity_id pm_package_activity_id
                           from location_matrix_packages lmp
                                    inner join package_matrix pm on lmp.package_matrix_id = pm.id
                                    inner join package_matrix pm1 on pm.project_id = pm1.project_id and
                                                                     pm.package_activity_id = pm1.package_activity_id and
                                                                     pm.package_id != pm1.package_id
                           where exists(select (1)
                                        from package_matrix pm2
                                        where pm.project_id = pm2.project_id
                                          and pm.package_activity_id = pm2.package_activity_id
                                          and pm.package_id != pm2.package_id
                                          and pm2.deleted is null)
                             and not exists(select (1)
                                 from location_matrix_packages lmp1
                                 where lmp1.location_matrix_id = lmp.location_matrix_id
                                   and lmp1.package_activity_id = lmp.package_activity_id
                                   and lmp1.package_id = pm1.package_id
                                   and lmp1.package_matrix_id = pm1.id)
                             and pm.deleted is not null)
                update location_matrix_packages
                set package_matrix_id=t.pm_id,
                    package_id=t.pm_package_id
                from t
                where location_matrix_packages.id = t.lmp_id
            """)
