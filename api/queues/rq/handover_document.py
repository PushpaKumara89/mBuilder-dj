from typing import List

from django_rq import job

from api.queues.core.handover_document import \
    create_handover_document_from_asset_handover_document_media as create_handover_document_from_asset_handover_document_media_core, \
    delete_handover_document_on_asset_handover_document_media_delete as delete_handover_document_on_asset_handover_document_media_delete_core, \
    delete_handover_document_on_asset_handover_delete as delete_handover_document_on_asset_handover_delete_core, \
    undelete_handover_document_on_asset_handover_undelete as undelete_handover_document_on_asset_handover_undelete_core, \
    undelete_handover_document_on_package_handover_undelete as undelete_handover_document_on_package_handover_undelete_core, \
    create_handover_document_from_package_handover_document_media as create_handover_document_from_package_handover_document_media_core, \
    delete_handover_document_on_package_handover_document_media_delete as delete_handover_document_on_package_handover_document_media_delete_core, \
    delete_handover_document_on_package_handover_delete as delete_handover_document_on_package_handover_delete_core, \
    delete_handover_document_on_package_handover_document_delete as delete_handover_document_on_package_handover_document_delete_core, \
    update_handover_document_on_asset_handover_document_media_update as update_handover_document_on_asset_handover_document_media_update_core, \
    update_handover_document_on_package_handover_document_media_update as update_handover_document_on_package_handover_document_media_update_core, \
    update_handover_document_on_location_matrix_update as update_handover_document_on_location_matrix_update_core, \
    remove_handover_document_on_asset_handover_document_media_update as remove_handover_document_on_asset_handover_document_media_update_core, \
    remove_handover_document_on_package_handover_document_media_update as remove_handover_document_on_package_handover_document_media_update_core, \
    create_handover_document_on_asset_handover_document_media_update as create_handover_document_on_asset_handover_document_media_update_core, \
    create_handover_document_on_package_handover_document_media_update as create_handover_document_on_package_handover_document_media_update_core, \
    send_email_with_handover_document_archive as send_email_with_handover_document_archive_core


from api.models import AssetHandoverDocumentMedia, AssetHandover, PackageHandoverDocumentMedia, PackageHandover, \
    AssetHandoverDocumentMediaUpdate, PackageHandoverDocumentMediaUpdate, LocationMatrix, Media, User, \
    PackageHandoverDocument


@job('handover_document', timeout=3600)
def create_handover_document_from_asset_handover_document_media(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    create_handover_document_from_asset_handover_document_media_core(asset_handover_document_media)


@job('handover_document', timeout=3600)
def delete_handover_document_on_asset_handover_document_media_delete(asset_handover_document_media: AssetHandoverDocumentMedia) -> None:
    delete_handover_document_on_asset_handover_document_media_delete_core(asset_handover_document_media)


@job('handover_document', timeout=3600)
def delete_handover_document_on_asset_handover_delete(asset_handover: AssetHandover) -> None:
    delete_handover_document_on_asset_handover_delete_core(asset_handover)


@job('handover_document', timeout=3600)
def undelete_handover_document_on_asset_handover_undelete(asset_handovers: List[AssetHandover]) -> None:
    undelete_handover_document_on_asset_handover_undelete_core(asset_handovers)


@job('handover_document', timeout=3600)
def undelete_handover_document_on_package_handover_undelete(package_handover: PackageHandover) -> None:
    undelete_handover_document_on_package_handover_undelete_core(package_handover)


@job('handover_document', timeout=3600)
def create_handover_document_from_package_handover_document_media(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    create_handover_document_from_package_handover_document_media_core(package_handover_document_media)


@job('handover_document', timeout=3600)
def delete_handover_document_on_package_handover_document_media_delete(package_handover_document_media: PackageHandoverDocumentMedia) -> None:
    delete_handover_document_on_package_handover_document_media_delete_core(package_handover_document_media)


@job('handover_document', timeout=3600)
def delete_handover_document_on_package_handover_delete(package_handover: PackageHandover) -> None:
    delete_handover_document_on_package_handover_delete_core(package_handover)


@job('handover_document', timeout=3600)
def delete_handover_document_on_package_handover_document_delete(package_handover_document: PackageHandoverDocument) -> None:
    delete_handover_document_on_package_handover_document_delete_core(package_handover_document)


@job('handover_document', timeout=3600)
def update_handover_document_on_asset_handover_document_media_update(asset_handover_document_media_update: AssetHandoverDocumentMediaUpdate) -> None:
    update_handover_document_on_asset_handover_document_media_update_core(asset_handover_document_media_update)


@job('handover_document', timeout=3600)
def update_handover_document_on_package_handover_document_media_update(package_handover_document_media_update: PackageHandoverDocumentMediaUpdate) -> None:
    update_handover_document_on_package_handover_document_media_update_core(package_handover_document_media_update)


@job('handover_document', timeout=3600)
def update_handover_document_on_location_matrix_update(location_matrices: List[LocationMatrix]) -> None:
    update_handover_document_on_location_matrix_update_core(location_matrices)


@job('handover_document', timeout=3600)
def remove_handover_document_on_asset_handover_document_media_update(update: AssetHandoverDocumentMediaUpdate) -> None:
    remove_handover_document_on_asset_handover_document_media_update_core(update)


@job('handover_document', timeout=3600)
def remove_handover_document_on_package_handover_document_media_update(update: PackageHandoverDocumentMediaUpdate) -> None:
    remove_handover_document_on_package_handover_document_media_update_core(update)


@job('handover_document', timeout=3600)
def create_handover_document_on_asset_handover_document_media_update(update: AssetHandoverDocumentMediaUpdate) -> None:
    create_handover_document_on_asset_handover_document_media_update_core(update)


@job('handover_document', timeout=3600)
def create_handover_document_on_package_handover_document_media_update(update: PackageHandoverDocumentMediaUpdate) -> None:
    create_handover_document_on_package_handover_document_media_update_core(update)


@job('handover_document', timeout=3600)
def send_email_with_handover_document_archive(archive: Media, project_id: int, user: User) -> None:
    send_email_with_handover_document_archive_core(archive, project_id, user)
