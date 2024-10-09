import ujson
from django.db import migrations, connection

from api.models import AssetHandoverDocumentMedia


def clear_asset_handover_statistics(*args, **kwargs):
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE ONLY asset_handover_statistics RESTART IDENTITY;")


def fill_asset_handover_statistics(*args, **kwargs):
    with connection.cursor() as cursor:
        project_ids = get_projects(cursor)
        for project_id in project_ids:
            project_id = project_id[0]
            files_statistics = fetch_uploaded_files_statistics(project_id, cursor)
            required_files_count, uploaded_files_count = files_statistics
            required_files_count = 0 if required_files_count is None else required_files_count
            uploaded_files_count = 0 if uploaded_files_count is None else uploaded_files_count
            statistics_by_statuses = fetch_statistics_by_statuses(project_id, cursor)
            formatted_stats_by_statuses = form_statistics_by_statuses(statistics_by_statuses)
            filled_information_count = fetch_filled_information(project_id, cursor)
            total_information_count = fetch_total_information(project_id, cursor)

            cursor.execute("""
                INSERT INTO asset_handover_statistics(project_id, required_files_count, uploaded_files_count, filled_info_count, total_info_count, statistics_by_statuses, created_at, updated_at)
                     VALUES (%s, %s, %s, %s, %s, %s, now(), now())
            """, (project_id, required_files_count, uploaded_files_count, filled_information_count, total_information_count, ujson.dumps(formatted_stats_by_statuses)))


def form_statistics_by_statuses(raw_statistics_by_statuses: list) -> dict:
    statuses = AssetHandoverDocumentMedia.Status.values
    stats_by_statuses = {status: 0 for status in statuses}
    for row in raw_statistics_by_statuses:
        stats_by_statuses[row[0]] = row[1]

    return stats_by_statuses


def fetch_filled_information(project_id: int, cursor):
    cursor.execute("""
        SELECT count(DISTINCT ahi.id) FROM asset_handover_information ahi
            INNER JOIN asset_handovers ah ON ah.id = ahi.asset_handover_id
            INNER JOIN (SELECT id FROM location_matrix WHERE project_id = %s AND deleted IS NULL) lm ON lm.id = ah.location_matrix_id
        WHERE ah.deleted IS NULL
          AND ahi.deleted IS NULL
          AND ahi.guid_external_ref IS NOT NULL
          AND ahi.warranty IS NOT NULL
          AND ahi.manufacture_serial_number IS NOT NULL
          AND ahi.model_number IS NOT NULL;
    """, (project_id, ))

    return cursor.fetchall()[0][0]


def fetch_total_information(project_id: int, cursor):
    cursor.execute("""
        SELECT count(DISTINCT ahi.id) FROM asset_handover_information ahi
            INNER JOIN asset_handovers ah ON ah.id = ahi.asset_handover_id
            INNER JOIN (SELECT id FROM location_matrix WHERE project_id = %s AND deleted IS NULL) lm ON lm.id = ah.location_matrix_id
        WHERE ah.deleted IS NULL
          AND ahi.deleted IS NULL;
    """, (project_id, ))

    return cursor.fetchall()[0][0]


def fetch_uploaded_files_statistics(project_id: int, cursor):
    cursor.execute("""
        SELECT sum(number_required_files) required_files_count, sum(media_count)::integer uploaded_files_count
        FROM (
                 SELECT ahd.id, min(ahd.number_required_files) number_required_files, count(ahdm.id) media_count
                 FROM asset_handover_documents ahd
                          LEFT JOIN asset_handover_document_media ahdm on ahd.id = ahdm.asset_handover_document_id
                          INNER JOIN asset_handovers ah on ah.id = ahd.asset_handover_id
                          INNER JOIN (SELECT id FROM location_matrix WHERE project_id = %s AND deleted IS NULL) lm ON lm.id = ah.location_matrix_id
                 WHERE ahdm.deleted IS NULL
                   AND ahd.deleted IS NULL
                 GROUP BY ahd.id
             ) uploaded_fiels_statistic
    """, (project_id, ))

    return cursor.fetchall()[0]


def fetch_statistics_by_statuses(project_id: int, cursor):
    cursor.execute("""
        SELECT status, COUNT(ahdm.id) media_count
        FROM asset_handover_document_media ahdm
                 INNER JOIN asset_handover_documents ahd ON ahd.id = ahdm.asset_handover_document_id
                 INNER JOIN asset_handovers ah ON ah.id = ahd.asset_handover_id
                 INNER JOIN (SELECT id FROM location_matrix WHERE project_id = %s AND deleted IS NULL) lm ON lm.id = ah.location_matrix_id
        WHERE ahdm.deleted IS NULL
          AND ahd.deleted IS NULL
        GROUP BY status
        ORDER BY status
    """, (project_id, ))

    return cursor.fetchall()


def get_projects(cursor):
    cursor.execute("SELECT id FROM projects")
    return cursor.fetchall()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0167_create_asset_handover_statistics_table_20220118_0944'),
    ]

    operations = [
        migrations.RunPython(code=fill_asset_handover_statistics, reverse_code=clear_asset_handover_statistics)
    ]
