from django.contrib.contenttypes.models import ContentType
from django.db import migrations, connection

from api.models import PackageHandoverDocumentMedia


def fill_handover_documents_from_package_handover_document_media(*args, **kwargs):
    with connection.cursor() as cursor:
        package_handover_document_media_content_type_id = ContentType.objects.get_for_model(PackageHandoverDocumentMedia).id
        projects = get_projects(cursor)
        for project_id in projects:
            insert_handover_documents(cursor, project_id[0], package_handover_document_media_content_type_id)


def get_projects(cursor) -> tuple:
    cursor.execute("""
        SELECT id FROM projects WHERE deleted IS NULL ORDER BY id;
    """)

    return cursor.fetchall()


def insert_handover_documents(cursor, project_id: int, package_handover_document_media_content_type_id: int) -> None:
    cursor.execute("""
        INSERT INTO handover_documents(object_id, building, level, area, package_activity_id, media_id, document_type,
                                       filename, uid, company_id, package_id, information, content_type_id, project_id,
                                       created_at, updated_at)
        SELECT document_media.id,
               location_matrix.building,
               location_matrix.level,
               location_matrix.area,
               package_matrix.package_activity_id,
               media.id,
               handover_documents.package_handover_document_type_id,
               media.name,
               document_media.uid,
               companies.id,
               package_matrix.package_id,
               information,
               %s,
               %s,
               now(),
               now()
        FROM package_handover_document_media document_media
                 INNER JOIN media ON media.id = document_media.media_id
                 INNER JOIN package_handover_documents handover_documents ON handover_documents.id = document_media.package_handover_document_id
                 INNER JOIN package_handovers ON package_handovers.id = handover_documents.package_handover_id
                 INNER JOIN (SELECT *
                             FROM package_handover_document_media_updates
                             WHERE package_handover_document_media_updates.id IN 
                                   (SELECT max(document_media_grouped_by_status.id)
                                    FROM package_handover_document_media_updates document_media_grouped_by_status
                                    WHERE (document_media_grouped_by_status.old_data -> 'status' !=
                                           document_media_grouped_by_status.new_data -> 'status')
                                       OR cast(document_media_grouped_by_status.old_data -> 'status' AS TEXT) IS NULL
                                    GROUP BY document_media_grouped_by_status.package_handover_document_media_id)) document_media_updates
                            ON document_media_updates.package_handover_document_media_id = document_media.id
                 INNER JOIN auth_user users ON users.id = document_media_updates.user_id
                 INNER JOIN companies ON users.company_id = companies.id
                 INNER JOIN package_matrix ON package_matrix.id = package_handovers.package_matrix_id
                 INNER JOIN location_matrix_packages lmp ON lmp.package_matrix_id = package_matrix.id
                 INNER JOIN location_matrix ON lmp.location_matrix_id = location_matrix.id
        WHERE document_media.status IN ('accepted', 'requesting_approval')
          AND document_media.deleted IS NULL
          AND package_matrix.project_id = %s
        ORDER BY document_media.id
    """, (package_handover_document_media_content_type_id, project_id, project_id))


def reverse_migration(*args, **kwargs):
    with connection.cursor() as cursor:
        package_handover_document_media_content_type_id = ContentType.objects.get_for_model(PackageHandoverDocumentMedia).id

        cursor.execute("""
            DELETE FROM handover_documents WHERE content_type_id = %s;            
        """, (package_handover_document_media_content_type_id,))


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0181_fill_handover_documents_from_asset_handover_document_media'),
    ]

    operations = [
        migrations.RunPython(code=fill_handover_documents_from_package_handover_document_media, reverse_code=reverse_migration),
    ]
