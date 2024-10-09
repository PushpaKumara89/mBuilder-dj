from django.contrib.contenttypes.models import ContentType
from django.db import migrations, connection

from api.models import AssetHandoverDocumentMedia


def fill_handover_documents_from_asset_handover_document_media(*args, **kwargs):
    with connection.cursor() as cursor:
        asset_handover_document_media_content_type_id = ContentType.objects.get_for_model(AssetHandoverDocumentMedia).id
        projects = get_projects(cursor)
        for project_id in projects:
            insert_handover_documents(cursor, project_id[0], asset_handover_document_media_content_type_id)


def get_projects(cursor) -> tuple:
    cursor.execute("""
        SELECT id FROM projects WHERE deleted IS NULL ORDER BY id;
    """)

    return cursor.fetchall()


def insert_handover_documents(cursor, project_id: int, asset_handover_document_media_content_type_id: int) -> None:
    cursor.execute("""
        INSERT INTO handover_documents(object_id, building, level, area, package_activity_id, media_id, document_type,
                                       filename, uid, company_id, package_id, information, content_type_id, project_id,
                                       created_at, updated_at)
        SELECT document_media.id,
               location_matrix.building,
               location_matrix.level,
               location_matrix.area,
               asset_handover.package_activity_id,
               media.id,
               documents.document_type_id,
               media.name,
               document_media.uid,
               companies.id,
               package_matrix.package_id,
               null,
               %s,
               %s,
               now(),
               now()
        FROM asset_handover_document_media document_media
                 INNER JOIN media ON media.id = document_media.media_id
                 INNER JOIN asset_handover_documents documents ON documents.id = document_media.asset_handover_document_id
                 INNER JOIN asset_handovers asset_handover ON asset_handover.id = documents.asset_handover_id
                 INNER JOIN location_matrix ON location_matrix.id = asset_handover.location_matrix_id
                 INNER JOIN (SELECT *
                             FROM asset_handover_document_media_updates
                             WHERE asset_handover_document_media_updates.id IN 
                                   (SELECT max(id)
                                    FROM asset_handover_document_media_updates document_media_grouped_by_status
                                    WHERE (document_media_grouped_by_status.old_data -> 'status' !=
                                           document_media_grouped_by_status.new_data -> 'status')
                                       OR cast(document_media_grouped_by_status.old_data -> 'status' AS TEXT) IS NULL
                                    GROUP BY document_media_grouped_by_status.asset_handover_document_media_id)) document_media_updates
                            ON document_media_updates.asset_handover_document_media_id = document_media.id
                 INNER JOIN auth_user users ON users.id = document_media_updates.user_id
                 INNER JOIN companies ON users.company_id = companies.id
                 INNER JOIN package_matrix ON package_matrix.package_activity_id = asset_handover.package_activity_id AND
                                              package_matrix.project_id = location_matrix.project_id
        WHERE document_media.status IN ('accepted', 'requesting_approval')
          AND document_media.deleted IS NULL
          AND package_matrix.project_id = %s
        ORDER BY document_media.id
    """, (asset_handover_document_media_content_type_id, project_id, project_id))


def reverse_migration(*args, **kwargs):
    with connection.cursor() as cursor:
        asset_handover_document_media_content_type_id = ContentType.objects.get_for_model(AssetHandoverDocumentMedia).id

        cursor.execute("""
            DELETE FROM handover_documents WHERE content_type_id = %s;            
        """, (asset_handover_document_media_content_type_id,))


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0180_create_handover_document'),
    ]

    operations = [
        migrations.RunPython(code=fill_handover_documents_from_asset_handover_document_media,
                             reverse_code=reverse_migration),
    ]
