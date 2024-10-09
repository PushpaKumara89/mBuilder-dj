from django_rq import job
from rq import Retry

from api.queues.core.package_handover_statistics import \
    create_statistics_on_package_handover_document_create as create_statistics_on_package_handover_document_create_core, \
    delete_statistics_on_package_handover_document_delete as delete_statistics_on_package_handover_document_delete_core, \
    undelete_statistics_on_package_handover_document_undelete as undelete_statistics_on_package_handover_document_undelete_core, \
    increase_statistics_for_document_media_status as increase_statistics_for_document_media_status_core, \
    decrease_statistics_for_document_media_status as decrease_statistics_for_document_media_status_core, \
    update_statistics_by_statuses_on_document_media_status_change as update_statistics_by_statuses_on_document_media_status_change_core, \
    delete_statistics_on_project_delete as delete_statistics_on_project_delete_core, \
    delete_statistics_on_package_handover_delete as delete_statistics_on_package_handover_delete_core, \
    undelete_statistics_on_package_handover_undelete as undelete_statistics_on_package_handover_undelete_core, \
    change_statistics_on_package_handover_document_media_update_create as change_statistics_on_package_handover_document_media_update_create_core

from api.models import PackageHandoverDocumentMedia, PackageHandoverDocument, Project, PackageHandover, \
    PackageHandoverDocumentMediaUpdate, User


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def create_statistics_on_package_handover_document_create(package_handover_document: PackageHandoverDocument) -> None:
    create_statistics_on_package_handover_document_create_core(package_handover_document)

@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def delete_statistics_on_package_handover_document_delete(package_handover_document: PackageHandoverDocument) -> None:
    delete_statistics_on_package_handover_document_delete_core(package_handover_document)


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def undelete_statistics_on_package_handover_document_undelete(package_handover_document: PackageHandoverDocument) -> None:
    undelete_statistics_on_package_handover_document_undelete_core(package_handover_document)


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def increase_statistics_for_document_media_status(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    increase_statistics_for_document_media_status_core(package_handover_document_media)


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def decrease_statistics_for_document_media_status(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    decrease_statistics_for_document_media_status_core(package_handover_document_media)


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def update_statistics_by_statuses_on_document_media_status_change(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    update_statistics_by_statuses_on_document_media_status_change_core(package_handover_document_media)


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def delete_statistics_on_project_delete(project: Project) -> None:
    delete_statistics_on_project_delete_core(project)


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def delete_statistics_on_package_handover_delete(package_handover: PackageHandover) -> None:
    delete_statistics_on_package_handover_delete_core(package_handover)


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def undelete_statistics_on_package_handover_undelete(package_handover: PackageHandover) -> None:
    undelete_statistics_on_package_handover_undelete_core(package_handover)


@job('package_handover_statistics', timeout=600, retry=Retry(max=3))
def change_statistics_on_package_handover_document_media_update_create(update: PackageHandoverDocumentMediaUpdate, user: User) -> None:
    change_statistics_on_package_handover_document_media_update_create_core(update, user)
