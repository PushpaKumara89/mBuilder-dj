# Generated by Django 3.2.4 on 2022-02-02 12:49

from django.db import migrations, connection


def create_missing_package_handovers(*args, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM projects ORDER BY id;")
        projects_id = cursor.fetchall()
        for project_id in projects_id:
            cursor.execute("""
                SELECT DISTINCT lmp.package_matrix_id FROM location_matrix_packages lmp
                        INNER JOIN package_matrix pm ON pm.id = lmp.package_matrix_id
                        LEFT JOIN package_handovers ph ON ph.package_matrix_id = pm.id
                WHERE lmp.deleted IS NULL
                  AND lmp.enabled
                  AND ph.id IS NULL
                  AND pm.deleted IS NULL
                  AND pm.project_id = %s;
            """, (project_id[0],))
            package_matrices_id = cursor.fetchall()
            for package_matrix_id in package_matrices_id:
                cursor.execute("""
                    INSERT INTO package_handovers(package_matrix_id, created_at, updated_at) VALUES (%s, now(), now());
                """, (package_matrix_id[0],))


def reverse_function(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0169_merge_20220202_1249'),
    ]

    operations = [
        migrations.RunPython(code=create_missing_package_handovers, reverse_code=reverse_function)
    ]
