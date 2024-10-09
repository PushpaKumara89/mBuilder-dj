from collections import namedtuple

import ujson
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, connection

from api.models import Project, PackageActivity

FilesStatisticsTuple = namedtuple('FilesStatistics', ('project', 'required_files_count', 'uploaded_files_count', 'total_information_count', 'filled_information_count'))
StatusStatisticsTuple = namedtuple('StatusesStatistics', ('project', 'statuses'))


def clear_asset_handover_statistics(*args, **kwargs):
    pass


class ProjectFilesStatistics:
    content_type: int
    project: int
    required_files_count: int = 0
    uploaded_files_count: int = 0
    total_information_count: int = 0
    filled_information_count: int = 0
    statistics_by_statuses: dict = {}

    def __init__(self, content_type_id: int):
        self.content_type = content_type_id

    def set_files_stats(self, files_stats: FilesStatisticsTuple) -> None:
        self.project = files_stats.project
        self.required_files_count = files_stats.required_files_count if files_stats.required_files_count else 0
        self.uploaded_files_count = files_stats.uploaded_files_count if files_stats.uploaded_files_count else 0
        self.total_information_count = files_stats.total_information_count if files_stats.total_information_count else 0
        self.filled_information_count = files_stats.filled_information_count if files_stats.filled_information_count else 0

    def set_statuses_statistics(self, stats: StatusStatisticsTuple) -> None:
        self.statistics_by_statuses = stats.statuses

    def to_tuple(self) -> tuple:
        return (self.project, self.content_type, self.project, self.required_files_count,
                self.uploaded_files_count, self.total_information_count, self.filled_information_count,
                ujson.dumps(self.statistics_by_statuses))


def fill_asset_handover_statistics(*args, **kwargs):
    with connection.cursor() as cursor:
        project_ids = get_projects(cursor)
        project_content_type_id = ContentType.objects.get_for_model(Project).id
        package_activity_content_type_id = ContentType.objects.get_for_model(PackageActivity).id

        for project_id in project_ids:
            empty_files_statistics_default_value = [(project_id, 0, 0, 0, 0)]
            empty_statistics_by_statuses_default_value = [(project_id, {})]
            project_id = project_id[0]
            files_statistics = fetch_uploaded_files_statistics_by_project(project_id, package_activity_content_type_id, cursor)

            if not files_statistics:
                files_statistics = empty_files_statistics_default_value

            files_statistics = FilesStatisticsTuple(*files_statistics[0])

            asset_handover_statistics = ProjectFilesStatistics(project_content_type_id)
            asset_handover_statistics.set_files_stats(files_statistics)

            statistics_by_statuses = fetch_statistics_by_statuses_by_project(project_id, package_activity_content_type_id, cursor)

            if not statistics_by_statuses:
                statistics_by_statuses = empty_statistics_by_statuses_default_value

            statistics_by_statuses = StatusStatisticsTuple(*statistics_by_statuses[0])
            if statistics_by_statuses:
                asset_handover_statistics.set_statuses_statistics(statistics_by_statuses)

            insert_asset_handover_statistics(asset_handover_statistics.to_tuple(), cursor)


def insert_asset_handover_statistics(rows, cursor):
    cursor.execute("""
        INSERT INTO asset_handover_statistics(project_id, content_type_id, object_id, required_files_count, uploaded_files_count, total_information_count, filled_information_count, statistics_by_statuses, created_at, updated_at)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), now())
    """, rows)


def fetch_uploaded_files_statistics_by_project(project_id: int, package_activity_content_type_id: int, cursor):
    cursor.execute("""
         SELECT project_id, sum(required_files_count), sum(uploaded_files_count), sum(total_information_count), sum(filled_information_count)
         FROM asset_handover_statistics
         WHERE content_type_id = %s
           AND deleted IS NULL
           AND project_id = %s
         GROUP BY project_id
    """, (package_activity_content_type_id, project_id, ))

    return cursor.fetchall()


def fetch_statistics_by_statuses_by_project(project_id: int, package_activity_content_type_id: int, cursor):
    cursor.execute("""
        SELECT project_id, json_object_agg(key, num)
        FROM (SELECT project_id, key, sum(value::integer) num
              FROM asset_handover_statistics ahs
                       INNER JOIN jsonb_each(statistics_by_statuses) ON true
              WHERE content_type_id = %s
                AND project_id = %s
                AND ahs.deleted IS NULL
              GROUP BY project_id, key) stats
        GROUP BY project_id;
    """, (package_activity_content_type_id, project_id))

    return cursor.fetchall()


def get_projects(cursor):
    cursor.execute("SELECT id FROM projects")
    return cursor.fetchall()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0178_initial_fill_asset_handover_statistics_table_for_package_activity_20220301_1725'),
    ]

    operations = [
        migrations.RunPython(code=fill_asset_handover_statistics, reverse_code=clear_asset_handover_statistics)
    ]
