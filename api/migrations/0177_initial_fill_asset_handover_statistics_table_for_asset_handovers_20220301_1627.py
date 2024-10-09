from collections import namedtuple
from typing import Optional

import pendulum
import ujson
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, connection
from pendulum import datetime

from api.models import AssetHandoverDocumentMedia, AssetHandover, AssetHandoverDocument

FilesStatisticsTuple = namedtuple('FilesStatistics', ('asset_handover', 'is_deleted', 'required_files_count', 'uploaded_files_count'))
StatusStatisticsTuple = namedtuple('StatusesStatistics', ('asset_handover', 'statuses'))


def clear_asset_handover_statistics(*args, **kwargs):
    pass


class AssetHandoverFilesStatistics:
    content_type: int
    project: int
    asset_handover: int
    deleted: Optional[datetime]
    required_files_count: int = 0
    uploaded_files_count: int = 0
    statistics_by_statuses: dict = {}

    def __init__(self, project_id: int, content_type_id: int):
        self.project = project_id
        self.content_type = content_type_id

    def set_files_stats(self, files_stats: FilesStatisticsTuple) -> None:
        self.asset_handover = files_stats.asset_handover
        self.deleted = pendulum.now() if files_stats.is_deleted else None
        self.required_files_count = files_stats.required_files_count if files_stats.required_files_count else 0
        self.uploaded_files_count = files_stats.uploaded_files_count if files_stats.uploaded_files_count else 0

    def set_statuses_statistics(self, stats: StatusStatisticsTuple) -> None:
        self.statistics_by_statuses = stats.statuses

    def to_tuple(self) -> tuple:
        return (self.project, self.content_type, self.asset_handover, self.required_files_count,
                self.uploaded_files_count, ujson.dumps(self.statistics_by_statuses), self.deleted)


def fill_asset_handover_statistics(*args, **kwargs):
    files_statistics_chunk_max_size = 500
    with connection.cursor() as cursor:
        project_ids = get_projects(cursor)
        asset_handover_document_content_type_id = ContentType.objects.get_for_model(AssetHandoverDocument).id
        asset_handover_content_type_id = ContentType.objects.get_for_model(AssetHandover).id

        for project_id in project_ids:
            project_id = project_id[0]
            files_statistics = fetch_uploaded_files_statistics_by_asset_handovers(project_id, cursor, asset_handover_document_content_type_id)
            statistics_by_statuses = fetch_statistics_by_statuses_by_asset_handovers(project_id, cursor, asset_handover_document_content_type_id)
            statistics_by_statuses = {statistic[0]: StatusStatisticsTuple(*statistic) for statistic in statistics_by_statuses}
            files_statistics_chunk = []
            for files_statistic in files_statistics:
                files_statistic = FilesStatisticsTuple(*files_statistic)
                doc_stats_by_status = statistics_by_statuses.get(files_statistic.asset_handover)
                asset_handover_statistics = AssetHandoverFilesStatistics(project_id, asset_handover_content_type_id)
                asset_handover_statistics.set_files_stats(files_statistic)

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
             VALUES (%s, %s, %s, %s, %s, %s, 0, 0, %s, now(), now())
    """, rows)


def form_statistics_by_statuses(raw_statistics_by_statuses: list) -> dict:
    statuses = AssetHandoverDocumentMedia.Status.values
    stats_by_statuses = {status: 0 for status in statuses}
    for row in raw_statistics_by_statuses:
        stats_by_statuses[row[0]] = row[1]

    return stats_by_statuses


def fetch_uploaded_files_statistics_by_asset_handovers(project_id: int, cursor, asset_handover_document_content_type_id: int):
    cursor.execute("""
        SELECT ah.id, bool_or(ahs.deleted is not null), sum(ahs.required_files_count), sum(ahs.uploaded_files_count)
        FROM asset_handover_documents ahd
                 INNER JOIN asset_handovers ah ON ah.id = ahd.asset_handover_id
                 INNER JOIN location_matrix lm ON lm.id = ah.location_matrix_id
                 INNER JOIN asset_handover_statistics ahs ON ahs.object_id = ahd.id
        WHERE lm.project_id = %s
          AND ahs.content_type_id = %s
        GROUP BY ah.id
    """, (project_id, asset_handover_document_content_type_id))

    return cursor.fetchall()


def fetch_statistics_by_statuses_by_asset_handovers(project_id: int, cursor, asset_handover_document_content_type_id: int):
    cursor.execute("""
        select ah_id, json_object_agg(key, num)
        from (select ahd.asset_handover_id ah_id, key, sum(value::integer) num
              from asset_handover_statistics ahs
                       inner join asset_handover_documents ahd on ahd.id = ahs.object_id
                       inner join jsonb_each(statistics_by_statuses::jsonb) on true
              where content_type_id = %s
                and project_id = %s
              group by ahd.asset_handover_id, key) stats
        group by ah_id;
    """, (asset_handover_document_content_type_id, project_id))

    return cursor.fetchall()


def get_projects(cursor):
    cursor.execute("SELECT id FROM projects")
    return cursor.fetchall()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0176_initial_fill_asset_handover_statistics_table_for_asset_handover_documents_20220225_1943'),
    ]

    operations = [
        migrations.RunPython(code=fill_asset_handover_statistics, reverse_code=clear_asset_handover_statistics)
    ]
