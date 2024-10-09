from collections import namedtuple
from typing import Optional

import pendulum
import ujson
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, connection
from pendulum import datetime

from api.models import PackageHandoverDocument


PackageHandoverDocumentFilesStatisticsTuple = namedtuple('FilesStatistics', ('package_handover_document', 'is_deleted', 'required_files_count', 'uploaded_files_count'))
StatusStatisticsTuple = namedtuple('StatusesStatistics', ('package_handover_document', 'statuses'))


class PackageHandoverDocumentFilesStatistics:
    content_type: int
    project: int
    package_handover_document: int
    required_files_count: int = 0
    uploaded_files_count: int = 0
    deleted: Optional[datetime]
    statistics_by_statuses: dict = {}

    def __init__(self, project_id: int, content_type_id: int):
        self.project = project_id
        self.content_type = content_type_id

    def set_files_stats(self, files_stats: PackageHandoverDocumentFilesStatisticsTuple) -> None:
        self.package_handover_document = files_stats.package_handover_document
        self.deleted = pendulum.now() if files_stats.is_deleted else None
        self.required_files_count = files_stats.required_files_count if files_stats.required_files_count else 0
        self.uploaded_files_count = files_stats.uploaded_files_count if files_stats.uploaded_files_count else 0

    def set_statuses_statistics(self, stats: StatusStatisticsTuple) -> None:
        self.statistics_by_statuses = stats.statuses

    def to_tuple(self) -> tuple:
        return (self.project, self.content_type, self.package_handover_document, self.required_files_count,
                self.uploaded_files_count, ujson.dumps(self.statistics_by_statuses), self.deleted)


def clear_package_handover_statistics(*args, **kwargs):
    pass


def fill_package_handover_statistics(*args, **kwargs):
    files_statistics_chunk_max_size = 500
    with connection.cursor() as cursor:
        project_ids = get_projects(cursor)
        package_handover_document_content_type_id = ContentType.objects.get_for_model(PackageHandoverDocument).id

        for project_id in project_ids:
            project_id = project_id[0]
            files_statistics = fetch_uploaded_files_statistics_by_package_handover_documents(project_id, cursor)
            statistics_by_statuses = fetch_statistics_by_statuses_by_package_handover_documents(project_id, cursor)
            statistics_by_statuses = {statistic[0]: StatusStatisticsTuple(*statistic) for statistic in statistics_by_statuses}
            files_statistics_chunk = []
            for files_statistic in files_statistics:
                files_statistic = PackageHandoverDocumentFilesStatisticsTuple(*files_statistic)
                doc_stats_by_status = statistics_by_statuses.get(files_statistic.package_handover_document)
                package_handover_statistics = PackageHandoverDocumentFilesStatistics(project_id, package_handover_document_content_type_id)
                package_handover_statistics.set_files_stats(files_statistic)

                if doc_stats_by_status:
                    package_handover_statistics.set_statuses_statistics(doc_stats_by_status)

                if len(files_statistics_chunk) == files_statistics_chunk_max_size:
                    insert_package_handover_document_statistics(files_statistics_chunk, cursor)
                    files_statistics_chunk.clear()
                else:
                    files_statistics_chunk.append(package_handover_statistics.to_tuple())

            if files_statistics_chunk:
                insert_package_handover_document_statistics(files_statistics_chunk, cursor)


def insert_package_handover_document_statistics(rows, cursor):
    cursor.executemany("""
        INSERT INTO package_handover_statistics(project_id, content_type_id, object_id, required_files_count, uploaded_files_count, statistics_by_statuses, deleted, created_at, updated_at)
             VALUES (%s, %s, %s, %s, %s, %s, %s, now(), now())
    """, rows)


def fetch_uploaded_files_statistics_by_package_handover_documents(project_id: int, cursor):
    cursor.execute("""
        SELECT phd.id,
               ((min(phd.deleted) IS NOT NULL) OR
                (min(ph.deleted) IS NOT NULL) OR
                (bool_and(pm.deleted IS NOT NULL))) is_deleted,
               min(phd.number_required_files),
               count(DISTINCT phdm.id) FILTER (WHERE phdm.deleted IS NULL)
        FROM package_handover_documents phd
                 LEFT JOIN package_handover_document_media phdm ON phd.id = phdm.package_handover_document_id
                 INNER JOIN package_handovers ph ON ph.id = phd.package_handover_id
                 INNER JOIN package_matrix pm ON ph.package_matrix_id = pm.id
        WHERE pm.project_id = %s
        GROUP BY phd.id
    """, (project_id,))

    return cursor.fetchall()


def fetch_statistics_by_statuses_by_package_handover_documents(project_id: int, cursor):
    cursor.execute("""
        SELECT phd_id, json_object_agg(status, media_count)
        FROM (SELECT phd.id phd_id, status, COUNT(phdm.id) media_count
              FROM package_handover_document_media phdm
                       INNER JOIN package_handover_documents phd ON phd.id = phdm.package_handover_document_id
                       INNER JOIN package_handovers ph ON ph.id = phd.package_handover_id
                       INNER JOIN package_matrix pm ON pm.id = ph.package_matrix_id
              WHERE phdm.deleted IS NULL
                AND pm.deleted IS NULL
              GROUP BY phd.id, status
              ORDER BY phd.id) stats
        GROUP BY stats.phd_id;
    """, (project_id,))

    return cursor.fetchall()


def get_projects(cursor):
    cursor.execute("SELECT id FROM projects")
    return cursor.fetchall()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0185_create_package_handover_statistics'),
    ]

    operations = [
        migrations.RunPython(code=fill_package_handover_statistics, reverse_code=clear_package_handover_statistics)
    ]
