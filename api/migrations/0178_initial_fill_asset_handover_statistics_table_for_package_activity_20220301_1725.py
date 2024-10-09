from collections import namedtuple
from typing import List, Optional

import pendulum
import ujson
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, connection
from pendulum import datetime

from api.models import PackageActivity, AssetHandover

FilesStatisticsTuple = namedtuple('FilesStatistics', (
    'package_activity', 'required_files_count', 'uploaded_files_count',
    'total_information_count', 'filled_information_count'
))
StatusStatisticsTuple = namedtuple('StatusesStatistics', ('package_activity', 'statuses'))
PackageActivityTuple = namedtuple('PackageActivity', ('package_activity', 'is_deleted'))


def clear_asset_handover_statistics(*args, **kwargs):
    pass


class PackageActivityFilesStatistics:
    content_type: int
    project: int
    package_activity: int
    deleted: Optional[datetime]
    total_information_count: int
    filled_information_count: int
    required_files_count: int = 0
    uploaded_files_count: int = 0
    statistics_by_statuses: dict = {}

    def __init__(self, project_id: int, content_type_id: int, is_deleted: bool):
        self.project = project_id
        self.content_type = content_type_id
        self.deleted = pendulum.now() if is_deleted else None

    def set_files_stats(self, files_stats: FilesStatisticsTuple) -> None:
        self.package_activity = files_stats.package_activity
        self.required_files_count = files_stats.required_files_count if files_stats.required_files_count else 0
        self.uploaded_files_count = files_stats.uploaded_files_count if files_stats.uploaded_files_count else 0
        self.total_information_count = files_stats.total_information_count
        self.filled_information_count = files_stats.filled_information_count

    def set_statuses_statistics(self, stats: StatusStatisticsTuple) -> None:
        self.statistics_by_statuses = stats.statuses

    def to_tuple(self) -> tuple:
        return (self.project, self.content_type, self.package_activity, self.required_files_count,
                self.uploaded_files_count, ujson.dumps(self.statistics_by_statuses),
                self.total_information_count, self.filled_information_count, self.deleted)


def fill_asset_handover_statistics(*args, **kwargs):
    with connection.cursor() as cursor:
        files_statistics_chunk_max_size = 500
        project_ids = get_projects(cursor)
        package_activity_content_type_id = ContentType.objects.get_for_model(PackageActivity).id
        asset_handover_content_type_id = ContentType.objects.get_for_model(AssetHandover).id

        for project_id in project_ids:
            files_statistics_chunk = []
            project_id = project_id[0]
            package_activities = fetch_project_package_activity(project_id, cursor)
            for package_activity in package_activities:
                files_statistics = fetch_uploaded_files_statistics_by_package_activity(project_id, package_activity.package_activity, asset_handover_content_type_id, cursor)
                doc_stats_by_status = fetch_statistics_by_statuses_by_package_activity(project_id, package_activity.package_activity, asset_handover_content_type_id, cursor)

                if not files_statistics:
                    continue

                asset_handover_statistics = PackageActivityFilesStatistics(project_id, package_activity_content_type_id, package_activity.is_deleted)
                asset_handover_statistics.set_files_stats(files_statistics)

                if doc_stats_by_status:
                    asset_handover_statistics.set_statuses_statistics(doc_stats_by_status)

                if len(files_statistics_chunk) == files_statistics_chunk_max_size:
                    insert_asset_handover_statistics(files_statistics_chunk, cursor)
                    files_statistics_chunk.clear()
                else:
                    files_statistics_chunk.append(asset_handover_statistics.to_tuple())

            if files_statistics_chunk:
                insert_asset_handover_statistics(files_statistics_chunk, cursor)


def insert_asset_handover_statistics(rows, cursor):
    cursor.executemany("""
        INSERT INTO asset_handover_statistics(project_id, content_type_id, object_id, required_files_count, uploaded_files_count, statistics_by_statuses, total_information_count, filled_information_count, deleted, created_at, updated_at)
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
    """, rows)


def fetch_uploaded_files_statistics_by_package_activity(project_id: int, package_activity_id: int, asset_handover_content_ype_id: int, cursor) -> FilesStatisticsTuple:
    cursor.execute("""
         SELECT ah.package_activity_id                                            pa_id,
               sum(ahs.required_files_count) FILTER ( WHERE ahs.deleted IS NULL ) required_files,
               sum(ahs.uploaded_files_count) FILTER ( WHERE ahs.deleted IS NULL ) uploaded_files,
               count(DISTINCT ahi.id)                                             total_info,
               count(DISTINCT ahi.id) FILTER ( WHERE ahi.guid_external_ref IS NOT NULL
                                               AND ahi.manufacture_serial_number IS NOT NULL
                                               AND ahi.model_number IS NOT NULL
                                               AND ahi.warranty IS NOT NULL )     filled_info
         FROM asset_handover_statistics ahs
                  INNER JOIN asset_handovers ah ON ah.id = ahs.object_id
                  INNER JOIN location_matrix lm ON lm.id = ah.location_matrix_id
                  INNER JOIN asset_handover_information ahi ON ah.id = ahi.asset_handover_id
         WHERE lm.project_id = %s
           AND ahs.content_type_id = %s
           AND ah.package_activity_id = %s
         GROUP BY ah.package_activity_id;
    """, (project_id, asset_handover_content_ype_id, package_activity_id))

    result = cursor.fetchall()

    return FilesStatisticsTuple(*result[0]) if result else None


def fetch_project_package_activity(project_id: int, cursor) -> List[PackageActivityTuple]:
    cursor.execute("""
         SELECT DISTINCT ON (pa.id) pa.id, pm.deleted IS NOT NULL
         FROM package_activities pa
              INNER JOIN package_matrix pm ON pm.package_activity_id = pa.id
         WHERE pm.project_id = %s
    """, (project_id, ))

    result = cursor.fetchall()

    return [PackageActivityTuple(*row) for row in result]


def fetch_statistics_by_statuses_by_package_activity(project_id: int, package_activity_id: int, asset_handover_content_type_id: int, cursor) -> Optional[StatusStatisticsTuple]:
    cursor.execute("""
        SELECT pa_id, json_object_agg(key, num)
        FROM (SELECT ah.package_activity_id pa_id, key, sum(value::integer) num
              FROM asset_handover_statistics ahs
                       INNER JOIN asset_handovers ah ON ah.id = ahs.object_id
                       INNER JOIN jsonb_each(statistics_by_statuses) ON true
              WHERE content_type_id = %s
                AND project_id = %s
                AND package_activity_id = %s
                AND ahs.deleted IS NULL
              GROUP BY ah.package_activity_id, key) stats
        GROUP BY pa_id;
    """, (asset_handover_content_type_id, project_id, package_activity_id))

    result = cursor.fetchall()

    return StatusStatisticsTuple(*result[0]) if result else None


def get_projects(cursor):
    cursor.execute("SELECT id FROM projects")
    return cursor.fetchall()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0177_initial_fill_asset_handover_statistics_table_for_asset_handovers_20220301_1627'),
    ]

    operations = [
        migrations.RunPython(code=fill_asset_handover_statistics, reverse_code=clear_asset_handover_statistics)
    ]
