from api.models import AssetHandover, AssetHandoverDocumentMedia, AssetHandoverDocument, PackageMatrix, Project, \
    AssetHandoverDocumentMediaUpdate, User
from api.services.asset_handover_statistics_service import AssetHandoverStatisticsService


def create_statistics_on_asset_handover_document_create(asset_handover_document: AssetHandoverDocument) -> None:
    AssetHandoverStatisticsService().create_on_asset_handover_document_create(asset_handover_document)


def update_statistics_on_document_update(asset_handover_document: AssetHandoverDocument) -> None:
    AssetHandoverStatisticsService().update_on_asset_handover_document_update(asset_handover_document)


def increase_statistics_for_document_media_status(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    AssetHandoverStatisticsService().increase_for_asset_handover_document_media_status(asset_handover_document_media)


def decrease_statistics_for_document_media_status(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    AssetHandoverStatisticsService().decrease_for_asset_handover_document_media_status(asset_handover_document_media)


def update_statistics_by_statuses_on_document_media_status_change(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    AssetHandoverStatisticsService().update_statistics_by_statuses_on_asset_handover_document_media_status_change(asset_handover_document_media)


def delete_statistics_on_asset_handover_delete(asset_handover: AssetHandover) -> None:
    AssetHandoverStatisticsService().delete_on_asset_handover_delete(asset_handover)


def undelete_statistics_on_asset_handover_undelete(asset_handover: list[AssetHandover]) -> None:
    AssetHandoverStatisticsService().undelete_on_asset_handover_undelete(asset_handover)


def delete_statistics_on_package_matrix_delete(package_matrix: PackageMatrix) -> None:
    AssetHandoverStatisticsService().delete_on_package_matrix_delete(package_matrix)


def undelete_statistics_on_package_matrix_undelete(package_matrix: PackageMatrix) -> None:
    AssetHandoverStatisticsService().undelete_on_package_matrix_undelete(package_matrix)


def delete_statistics_on_project_delete(project: Project) -> None:
    AssetHandoverStatisticsService().delete_on_project_delete(project)


def change_statistics_on_asset_handover_document_media_update_create(update: AssetHandoverDocumentMediaUpdate, user: User) -> None:
    AssetHandoverStatisticsService().change_on_asset_handover_document_media_update(update, user)
