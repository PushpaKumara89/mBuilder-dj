from collections import namedtuple
from typing import Optional

import pendulum
import ujson
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, connection
from pendulum import datetime

from api.models import AssetHandoverDocument


AssetHandoverDocumentFilesStatisticsTuple = namedtuple('FilesStatistics', ('asset_handover_document', 'is_deleted', 'required_files_count', 'uploaded_files_count'))
StatusStatisticsTuple = namedtuple('StatusesStatistics', ('asset_handover_document', 'statuses'))


class AssetHandoverDocumentFilesStatistics:
    content_type: int
    project: int
    asset_handover_document: int
    required_files_count: int = 0
    uploaded_files_count: int = 0
    deleted: Optional[datetime]
    statistics_by_statuses: dict = {}

    def __init__(self, project_id: int, content_type_id: int):
        self.project = project_id
        self.content_type = content_type_id

    def set_files_stats(self, files_stats: AssetHandoverDocumentFilesStatisticsTuple) -> None:
        self.asset_handover_document = files_stats.asset_handover_document
        self.deleted = pendulum.now() if files_stats.is_deleted else None
        self.required_files_count = files_stats.required_files_count if files_stats.required_files_count else 0
        self.uploaded_files_count = files_stats.uploaded_files_count if files_stats.uploaded_files_count else 0

    def set_statuses_statistics(self, stats: StatusStatisticsTuple) -> None:
        self.statistics_by_statuses = stats.statuses

    def to_tuple(self) -> tuple:
        return (self.project, self.content_type, self.asset_handover_document, self.required_files_count,
                self.uploaded_files_count, ujson.dumps(self.statistics_by_statuses), self.deleted)


def clear_asset_handover_statistics(*args, **kwargs):
    pass


def fill_asset_handover_statistics(*args, **kwargs):
    files_statistics_chunk_max_size = 500
    with connection.cursor() as cursor:
        project_ids = get_projects(cursor)
        asset_handover_document_content_type_id = ContentType.objects.get_for_model(AssetHandoverDocument).id

        for project_id in project_ids:
            project_id = project_id[0]
            files_statistics = fetch_uploaded_files_statistics_by_asset_handover_documents(project_id, cursor)
            statistics_by_statuses = fetch_statistics_by_statuses_by_asset_handover_documents(project_id, cursor)
            statistics_by_statuses = {statistic[0]: StatusStatisticsTuple(*statistic) for statistic in statistics_by_statuses}
            files_statistics_chunk = []
            for files_statistic in files_statistics:
                files_statistic = AssetHandoverDocumentFilesStatisticsTuple(*files_statistic)
                doc_stats_by_status = statistics_by_statuses.get(files_statistic.asset_handover_document)
                asset_handover_statistics = AssetHandoverDocumentFilesStatistics(project_id, asset_handover_document_content_type_id)
                asset_handover_statistics.set_files_stats(files_statistic)

                if doc_stats_by_status:
                    asset_handover_statistics.set_statuses_statistics(doc_stats_by_status)

                if len(files_statistics_chunk) == files_statistics_chunk_max_size:
                    insert_asset_handover_document_statistics(files_statistics_chunk, cursor)
                    files_statistics_chunk.clear()
                else:
                    files_statistics_chunk.append(asset_handover_statistics.to_tuple())

            if files_statistics_chunk:
                insert_asset_handover_document_statistics(files_statistics_chunk, cursor)


def insert_asset_handover_document_statistics(rows, cursor):
    cursor.executemany("""
        INSERT INTO asset_handover_statistics(project_id, content_type_id, object_id, required_files_count, uploaded_files_count, statistics_by_statuses, filled_information_count, total_information_count, deleted, created_at, updated_at)
             VALUES (%s, %s, %s, %s, %s, %s, 0, 0, %s, now(), now())
    """, rows)


def fetch_uploaded_files_statistics_by_asset_handover_documents(project_id: int, cursor):
    cursor.execute("""
        SELECT ahd.id,
               ((min(ahd.deleted) IS NOT NULL) OR
                (min(ah.deleted) IS NOT NULL) OR
                (min(lm.deleted) IS NOT NULL) OR
                (bool_and(pm.deleted IS NOT NULL))) is_deleted,
               min(ahd.number_required_files),
               count(DISTINCT ahdm.id) FILTER (WHERE ahdm.deleted IS NULL)
        FROM asset_handover_documents ahd
                 LEFT JOIN asset_handover_document_media ahdm ON ahd.id = ahdm.asset_handover_document_id
                 INNER JOIN asset_handovers ah ON ah.id = ahd.asset_handover_id
                 INNER JOIN location_matrix lm ON lm.id = ah.location_matrix_id
                 INNER JOIN package_matrix pm ON ah.package_activity_id = pm.package_activity_id
        WHERE lm.project_id = %s
          AND pm.project_id = lm.project_id
        GROUP BY ahd.id
    """, (project_id, ))

    return cursor.fetchall()


def fetch_statistics_by_statuses_by_asset_handover_documents(project_id: int, cursor):
    cursor.execute("""
        SELECT ahd_id, json_object_agg(status, media_count)
        FROM (SELECT ahd.id ahd_id, status, COUNT(ahdm.id) media_count
              FROM asset_handover_document_media ahdm
                       INNER JOIN asset_handover_documents ahd ON ahd.id = ahdm.asset_handover_document_id
                       INNER JOIN asset_handovers ah ON ah.id = ahd.asset_handover_id
                       INNER JOIN (SELECT id FROM location_matrix WHERE project_id = %s AND deleted IS NULL) lm ON lm.id = ah.location_matrix_id
              WHERE ahdm.deleted IS NULL
              GROUP BY ahd.id, status
              ORDER BY ahd.id) stats
        GROUP BY stats.ahd_id;
    """, (project_id, ))

    return cursor.fetchall()


def get_projects(cursor):
    cursor.execute("SELECT id FROM projects")
    return cursor.fetchall()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0175_recreate_asset_handover_statistics_20220301_0912'),
    ]

    operations = [
        migrations.RunPython(code=fill_asset_handover_statistics, reverse_code=clear_asset_handover_statistics)
    ]
