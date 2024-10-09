from api.models import PackageHandoverDocumentMedia, PackageHandoverDocument, Project, PackageHandover, \
    PackageHandoverDocumentMediaUpdate, User
from api.services.package_handover_statistics_service import PackageHandoverStatisticsService


def create_statistics_on_package_handover_document_create(package_handover_document: PackageHandoverDocument) -> None:
    PackageHandoverStatisticsService().create_on_package_handover_document_create(package_handover_document)


def delete_statistics_on_package_handover_document_delete(package_handover_document: PackageHandoverDocument) -> None:
    PackageHandoverStatisticsService().delete_on_package_handover_document_delete(package_handover_document)


def undelete_statistics_on_package_handover_document_undelete(package_handover_document: PackageHandoverDocument) -> None:
    PackageHandoverStatisticsService().undelete_on_package_handover_document_undelete(package_handover_document)


def increase_statistics_for_document_media_status(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    PackageHandoverStatisticsService().increase_for_package_handover_document_media_status(package_handover_document_media)


def decrease_statistics_for_document_media_status(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    PackageHandoverStatisticsService().decrease_for_package_handover_document_media_status(package_handover_document_media)


def update_statistics_by_statuses_on_document_media_status_change(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    PackageHandoverStatisticsService().update_statistics_by_statuses_on_package_handover_document_media_status_change(package_handover_document_media)


def delete_statistics_on_project_delete(project: Project) -> None:
    PackageHandoverStatisticsService().delete_on_project_delete(project)


def delete_statistics_on_package_handover_delete(package_handover: PackageHandover) -> None:
    PackageHandoverStatisticsService().delete_on_package_handover_delete(package_handover)


def undelete_statistics_on_package_handover_undelete(package_handover: PackageHandover) -> None:
    PackageHandoverStatisticsService().undelete_on_package_handover_undelete(package_handover)


def change_statistics_on_package_handover_document_media_update_create(update: PackageHandoverDocumentMediaUpdate, user: User) -> None:
    PackageHandoverStatisticsService().change_on_package_handover_document_media_update(update, user)
