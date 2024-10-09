from mbuild.settings import app as celery_app

from api.queues.core.asset_handover_statistics import \
    create_statistics_on_asset_handover_document_create as create_statistics_on_asset_handover_document_create_core, \
    update_statistics_on_document_update as update_statistics_on_document_update_core, \
    increase_statistics_for_document_media_status as increase_statistics_for_document_media_status_core, \
    decrease_statistics_for_document_media_status as decrease_statistics_for_document_media_status_core, \
    update_statistics_by_statuses_on_document_media_status_change as update_statistics_by_statuses_on_document_media_status_change_core, \
    delete_statistics_on_asset_handover_delete as delete_statistics_on_asset_handover_delete_core, \
    undelete_statistics_on_asset_handover_undelete as undelete_statistics_on_asset_handover_undelete_core, \
    delete_statistics_on_package_matrix_delete as delete_statistics_on_package_matrix_delete_core, \
    undelete_statistics_on_package_matrix_undelete as undelete_statistics_on_package_matrix_undelete_core, \
    delete_statistics_on_project_delete as delete_statistics_on_project_delete_core, \
    change_statistics_on_asset_handover_document_media_update_create as change_statistics_on_asset_handover_document_media_update_create_core

from api.models import AssetHandover, AssetHandoverDocumentMedia, AssetHandoverDocument, PackageMatrix, Project, \
    AssetHandoverDocumentMediaUpdate, User


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def create_statistics_on_asset_handover_document_create(asset_handover_document: AssetHandoverDocument) -> None:
    create_statistics_on_asset_handover_document_create_core(asset_handover_document)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def update_statistics_on_document_update(asset_handover_document: AssetHandoverDocument) -> None:
    update_statistics_on_document_update_core(asset_handover_document)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def increase_statistics_for_document_media_status(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    increase_statistics_for_document_media_status_core(asset_handover_document_media)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def decrease_statistics_for_document_media_status(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    decrease_statistics_for_document_media_status_core(asset_handover_document_media)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def update_statistics_by_statuses_on_document_media_status_change(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    update_statistics_by_statuses_on_document_media_status_change_core(asset_handover_document_media)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def delete_statistics_on_asset_handover_delete(asset_handover: AssetHandover) -> None:
    delete_statistics_on_asset_handover_delete_core(asset_handover)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def undelete_statistics_on_asset_handover_undelete(asset_handover: list[AssetHandover]) -> None:
    undelete_statistics_on_asset_handover_undelete_core(asset_handover)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def delete_statistics_on_package_matrix_delete(package_matrix: PackageMatrix) -> None:
    delete_statistics_on_package_matrix_delete_core(package_matrix)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def undelete_statistics_on_package_matrix_undelete(package_matrix: PackageMatrix) -> None:
    undelete_statistics_on_package_matrix_undelete_core(package_matrix)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def delete_statistics_on_project_delete(project: Project) -> None:
    delete_statistics_on_project_delete_core(project)


@celery_app.task(queue='asset_handover_statistics', time_limit=600)
def change_statistics_on_asset_handover_document_media_update_create(update: AssetHandoverDocumentMediaUpdate, user: User) -> None:
    change_statistics_on_asset_handover_document_media_update_create_core(update, user)
