from typing import List

from api.models import AssetHandoverDocumentMedia, AssetHandover, PackageHandoverDocumentMedia, PackageHandover, \
    AssetHandoverDocumentMediaUpdate, PackageHandoverDocumentMediaUpdate, LocationMatrix, Media, User, \
    PackageHandoverDocument
from api.services.handover_document_media_download_service import HandoverDocumentMediaDownloadService

from api.services.handover_document_service import HandoverDocumentService


def create_handover_document_from_asset_handover_document_media(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    HandoverDocumentService().create_from_asset_handover_document_media(asset_handover_document_media)


def delete_handover_document_on_asset_handover_document_media_delete(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    HandoverDocumentService().delete_on_asset_handover_document_media_delete(asset_handover_document_media)


def delete_handover_document_on_asset_handover_delete(asset_handover: AssetHandover) -> None:
    HandoverDocumentService().delete_on_asset_handover_delete(asset_handover)


def undelete_handover_document_on_asset_handover_undelete(asset_handovers: List[AssetHandover]) -> None:
    HandoverDocumentService().undelete_on_asset_handover_undelete(asset_handovers)


def undelete_handover_document_on_package_handover_undelete(package_handover: PackageHandover) -> None:
    HandoverDocumentService().undelete_on_package_handover_undelete(package_handover)


def create_handover_document_from_package_handover_document_media(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    HandoverDocumentService().create_from_package_handover_document_media(package_handover_document_media)


def delete_handover_document_on_package_handover_document_media_delete(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    HandoverDocumentService().delete_on_package_handover_document_media_delete(package_handover_document_media)


def delete_handover_document_on_package_handover_delete(package_handover: PackageHandover) -> None:
    HandoverDocumentService().delete_on_package_handover_delete(package_handover)


def delete_handover_document_on_package_handover_document_delete(package_handover_document: PackageHandoverDocument) -> None:
    HandoverDocumentService().delete_on_package_handover_document_delete(package_handover_document)


def update_handover_document_on_asset_handover_document_media_update(asset_handover_document_media_update: AssetHandoverDocumentMediaUpdate) -> None:
    HandoverDocumentService().update_on_asset_handover_document_media_update(asset_handover_document_media_update)


def update_handover_document_on_package_handover_document_media_update(package_handover_document_media_update: PackageHandoverDocumentMediaUpdate) -> None:
    HandoverDocumentService().update_on_package_handover_document_media_update(package_handover_document_media_update)


def update_handover_document_on_location_matrix_update(location_matrices: List[LocationMatrix]) -> None:
    HandoverDocumentService().update_on_location_matrix_update(location_matrices)


def remove_handover_document_on_asset_handover_document_media_update(update: AssetHandoverDocumentMediaUpdate) -> None:
    HandoverDocumentService().delete_on_asset_handover_document_status_change(update)


def remove_handover_document_on_package_handover_document_media_update(update: PackageHandoverDocumentMediaUpdate) -> None:
    HandoverDocumentService().delete_on_package_handover_document_status_change(update)


def create_handover_document_on_asset_handover_document_media_update(update: AssetHandoverDocumentMediaUpdate) -> None:
    HandoverDocumentService().create_on_asset_handover_document_status_change(update)


def create_handover_document_on_package_handover_document_media_update(update: PackageHandoverDocumentMediaUpdate) -> None:
    HandoverDocumentService().create_on_package_handover_document_status_change(update)


def send_email_with_handover_document_archive(archive: Media, project_id: int, user: User) -> None:
    HandoverDocumentMediaDownloadService().send_email_with_archive(archive, project_id, user)
