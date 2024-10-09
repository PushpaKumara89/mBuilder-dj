from io import BytesIO
from typing import List, Union
from zipfile import ZipFile, ZIP_DEFLATED

import pendulum
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import F, Q

from api.models import HandoverDocument, AssetHandoverDocumentMedia, LocationMatrixPackage, \
    AssetHandoverDocumentMediaUpdate, AssetHandover, PackageHandoverDocumentMedia, PackageHandoverDocumentMediaUpdate, \
    PackageHandover, Media, LocationMatrix, PackageHandoverDocument
from api.storages import AzurePrivateMediaStorage


class HandoverDocumentService:
    asset_handover_document_media_valid_statuses = (
        AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        AssetHandoverDocumentMedia.Status.ACCEPTED,
    )

    package_handover_document_media_valid_statuses = (
        PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        PackageHandoverDocumentMedia.Status.ACCEPTED,
    )

    def create_from_asset_handover_document_media(self, document_media: AssetHandoverDocumentMedia) -> None:
        document_media = AssetHandoverDocumentMedia.objects.select_related(
            'asset_handover_document__asset_handover__location_matrix__project'
        ).filter(id=document_media.id).get()
        asset_handover = document_media.asset_handover_document.asset_handover
        project = asset_handover.project
        package_activity = asset_handover.package_activity
        package = LocationMatrixPackage.objects.filter(
            location_matrix__project=project,
            location_matrix=asset_handover.location_matrix,
            package_activity=package_activity
        ).get().package
        last_update = AssetHandoverDocumentMediaUpdate.objects.filter(
            Q(~Q(old_data__media=F('new_data__media')) | Q(old_data={}, new_data__media__isnull=False)),
            asset_handover_document_media=document_media,
            new_data__media=document_media.media_id,
        ).order_by('-created_at').first()
        document_type = document_media.asset_handover_document.document_type.id
        handover_document = HandoverDocument.all_objects.filter(
            entity_id=document_media.id,
            entity=HandoverDocument.Entities.ASSET_HANDOVER
        ).first()

        if handover_document is None:
            HandoverDocument.objects.create(
                building=asset_handover.location_matrix.building,
                level=asset_handover.location_matrix.level,
                area=asset_handover.location_matrix.area,
                company=last_update.user.company,
                document_type=document_type,
                filename=document_media.media.name,
                media=document_media.media,
                entity_id=document_media.id,
                package=package,
                package_activity=package_activity,
                project=project,
                uid=document_media.uid,
                entity=HandoverDocument.Entities.ASSET_HANDOVER
            )
        elif handover_document.deleted:
            handover_document.undelete()

    def delete_on_asset_handover_document_media_delete(self, document_media: AssetHandoverDocumentMedia) -> None:
        HandoverDocument.objects.filter(
            entity=HandoverDocument.Entities.ASSET_HANDOVER,
            entity_id=document_media.id
        ).delete()

    def delete_on_asset_handover_delete(self, asset_handover: AssetHandover) -> None:
        document_media = list(AssetHandoverDocumentMedia.objects.filter(
            asset_handover_document__asset_handover=asset_handover
        ).values_list('id', flat=True))
        HandoverDocument.objects.filter(
            entity=HandoverDocument.Entities.ASSET_HANDOVER,
            entity_id__in=document_media
        ).delete()

    def undelete_on_asset_handover_undelete(self, asset_handovers: List[AssetHandover]) -> None:
        asset_handovers_ids = [asset_handover.id for asset_handover in asset_handovers]
        document_media = list(AssetHandoverDocumentMedia.objects.filter(
            asset_handover_document__asset_handover_id__in=asset_handovers_ids
        ).values_list('id', flat=True))
        HandoverDocument.deleted_objects.filter(
            entity=HandoverDocument.Entities.ASSET_HANDOVER,
            entity_id__in=document_media
        ).undelete()

    def undelete_on_package_handover_undelete(self, package_handover: PackageHandover) -> None:
        document_media = list(PackageHandoverDocumentMedia.objects.filter(
            package_handover_document__package_handover=package_handover
        ).values_list('id', flat=True))
        HandoverDocument.deleted_objects.filter(
            entity=HandoverDocument.Entities.PACKAGE_HANDOVER,
            entity_id__in=document_media
        ).update(package=package_handover.package_matrix.package, deleted=None)

    def create_from_package_handover_document_media(self, document_media: PackageHandoverDocumentMedia) -> None:
        document_media = PackageHandoverDocumentMedia.objects.select_related(
            'media',
            'package_handover_document__package_handover__package_matrix',
            'package_handover_document__package_activity'
        ).filter(id=document_media.id).first()
        if not document_media:
            return None
        project = document_media.package_handover_document.project
        package_activity = document_media.package_handover_document.package_activity
        package = document_media.package_handover_document.package_handover.package_matrix.package
        last_update = PackageHandoverDocumentMediaUpdate.objects.select_related('user__company').filter(
            Q(~Q(old_data__media=F('new_data__media')) | Q(old_data={}, new_data__media__isnull=False)),
            package_handover_document_media=document_media,
            new_data__media=document_media.media_id
        ).order_by('-created_at').first()
        document_type = document_media.package_handover_document.package_handover_document_type.id
        handover_document = HandoverDocument.all_objects.filter(
            entity_id=document_media.id,
            entity=HandoverDocument.Entities.PACKAGE_HANDOVER
        ).first()

        if handover_document is None:
            HandoverDocument.objects.create(
                building=None,
                level=None,
                area=None,
                company=last_update.user.company,
                document_type=document_type,
                filename=document_media.media.name,
                media=document_media.media,
                entity_id=document_media.id,
                package=package,
                package_activity=package_activity,
                project=project,
                uid=document_media.uid,
                entity=HandoverDocument.Entities.PACKAGE_HANDOVER,
                information=document_media.information
            )
        elif handover_document.deleted:
            handover_document.undelete()

    def delete_on_package_handover_document_media_delete(self, package_handover_document_media: PackageHandoverDocumentMedia) -> None:
        HandoverDocument.objects.filter(
            entity=HandoverDocument.Entities.PACKAGE_HANDOVER,
            entity_id=package_handover_document_media.id
        ).delete()

    def delete_on_package_handover_delete(self, package_handover: PackageHandover) -> None:
        package_handover_document_media_ids = list(
            PackageHandoverDocumentMedia.objects.filter(
                package_handover_document__package_handover=package_handover
            ).values_list('id', flat=True)
        )
        HandoverDocument.objects.filter(
            entity=HandoverDocument.Entities.PACKAGE_HANDOVER,
            entity_id__in=package_handover_document_media_ids
        ).delete()

    def delete_on_package_handover_document_delete(self, package_handover_document: PackageHandoverDocument) -> None:
        package_handover_document_media_ids = list(
            PackageHandoverDocumentMedia.objects.filter(
                package_handover_document=package_handover_document
            ).values_list('id', flat=True)
        )
        HandoverDocument.objects.filter(
            entity=HandoverDocument.Entities.PACKAGE_HANDOVER,
            entity_id__in=package_handover_document_media_ids
        ).delete()

    def update_on_asset_handover_document_media_update(self, asset_handover_document_media_update: AssetHandoverDocumentMediaUpdate) -> None:
        changed_fields = {}

        if 'uid' in asset_handover_document_media_update.new_data:
            changed_fields['uid'] = asset_handover_document_media_update.new_data['uid']

        if 'media' in asset_handover_document_media_update.new_data:
            changed_fields['company'] = asset_handover_document_media_update.user.company
            media = Media.objects.filter(id=asset_handover_document_media_update.new_data['media']).get()
            changed_fields['filename'] = media.name
            changed_fields['media'] = media

        if changed_fields:
            HandoverDocument.all_objects.filter(
                entity_id=asset_handover_document_media_update.asset_handover_document_media_id,
                entity=HandoverDocument.Entities.ASSET_HANDOVER
            ).update(**changed_fields)

    def update_on_package_handover_document_media_update(self, package_handover_document_media_update: PackageHandoverDocumentMediaUpdate) -> None:
        changed_fields = {}

        if 'uid' in package_handover_document_media_update.new_data:
            changed_fields['uid'] = package_handover_document_media_update.new_data['uid']

        if 'information' in package_handover_document_media_update.new_data:
            changed_fields['information'] = package_handover_document_media_update.new_data['information']

        if 'media' in package_handover_document_media_update.new_data:
            changed_fields['company'] = package_handover_document_media_update.user.company
            media = Media.objects.filter(id=package_handover_document_media_update.new_data['media']).get()
            changed_fields['filename'] = media.name
            changed_fields['media'] = media

        if changed_fields:
            HandoverDocument.all_objects.filter(
                entity_id=package_handover_document_media_update.package_handover_document_media_id,
                entity=HandoverDocument.Entities.PACKAGE_HANDOVER
            ).update(**changed_fields)

    def update_on_location_matrix_update(self, location_matrices: List[LocationMatrix]) -> None:
        for location_matrix in location_matrices:
            asset_handover_document_media = list(AssetHandoverDocumentMedia.objects.filter(
                asset_handover_document__asset_handover__location_matrix_id=location_matrix.id
            ).values_list('id', flat=True))

            HandoverDocument.objects.filter(
                entity_id__in=asset_handover_document_media,
                entity=HandoverDocument.Entities.ASSET_HANDOVER
            ).update(
                building=location_matrix.building,
                level=location_matrix.level,
                area=location_matrix.area
            )

    def delete_on_asset_handover_document_status_change(self, update: AssetHandoverDocumentMediaUpdate) -> None:
        HandoverDocument.objects.filter(
            entity=HandoverDocument.Entities.ASSET_HANDOVER,
            entity_id=update.asset_handover_document_media_id
        ).delete()

    def delete_on_package_handover_document_status_change(self, update: PackageHandoverDocumentMediaUpdate) -> None:
        HandoverDocument.objects.filter(
            entity=HandoverDocument.Entities.PACKAGE_HANDOVER,
            entity_id=update.package_handover_document_media_id
        ).delete()

    def create_on_asset_handover_document_status_change(self, update: AssetHandoverDocumentMediaUpdate) -> None:
        self.create_from_asset_handover_document_media(update.asset_handover_document_media)

    def create_on_package_handover_document_status_change(self, update: PackageHandoverDocumentMediaUpdate) -> None:
        self.create_from_package_handover_document_media(update.package_handover_document_media)

    def get_archive_with_media_to_save(self, data: dict) -> dict:
        archive = self.__generate_archive(data)
        filename = self.__generate_archive_name()
        uploaded_file = SimpleUploadedFile(content=archive, name=filename, content_type='application/zip')

        return {
            'file': uploaded_file,
            'is_public': False
        }

    @classmethod
    def can_create_from_asset_handover_document_media(cls, asset_handover_document_media: AssetHandoverDocumentMedia) -> bool:
        return asset_handover_document_media.status in cls.asset_handover_document_media_valid_statuses

    @classmethod
    def can_create_from_package_handover_document_media(cls, package_handover_document_media: PackageHandoverDocumentMedia) -> bool:
        return package_handover_document_media.status in cls.package_handover_document_media_valid_statuses

    @classmethod
    def need_to_remove_asset_handover_document_media(cls, update: AssetHandoverDocumentMediaUpdate) -> bool:
        return cls.__need_to_remove_from_handover_document(update, cls.asset_handover_document_media_valid_statuses)

    @classmethod
    def need_to_remove_package_handover_document_media(cls, update: PackageHandoverDocumentMediaUpdate) -> bool:
        return cls.__need_to_remove_from_handover_document(update, cls.package_handover_document_media_valid_statuses)

    @classmethod
    def need_to_create_from_asset_handover_document_media(cls, update: AssetHandoverDocumentMediaUpdate) -> bool:
        return cls.__need_to_create_handover_document(update, cls.asset_handover_document_media_valid_statuses)

    @classmethod
    def need_to_create_from_package_handover_document_media(cls, update: PackageHandoverDocumentMediaUpdate) -> bool:
        return cls.__need_to_create_handover_document(update, cls.package_handover_document_media_valid_statuses)

    def __generate_archive_name(self):
        return 'handover_document_report_%s.zip' % pendulum.now().to_datetime_string()

    def __generate_archive(self, data: dict) -> bytes:
        handover_documents = data['handover_document']
        handover_document_ids = [handover_document.media.id for handover_document in handover_documents]
        handover_document_media = Media.objects.filter(id__in=handover_document_ids).all()
        zip_file = BytesIO()
        storage = AzurePrivateMediaStorage()

        with ZipFile(zip_file, 'w', compression=ZIP_DEFLATED) as archive:
            for media in handover_document_media:
                downloaded_file = storage.open(media.original_link)
                archive.writestr(media.name, downloaded_file.file.read())

        return zip_file.getvalue()

    @classmethod
    def __need_to_remove_from_handover_document(
            cls,
            update: Union[PackageHandoverDocumentMediaUpdate, AssetHandoverDocumentMediaUpdate],
            handover_document_valid_statuses
    ) -> bool:
        return 'status' in update.old_data and \
               update.old_data['status'] in handover_document_valid_statuses and \
               update.new_data['status'] not in handover_document_valid_statuses

    @classmethod
    def __need_to_create_handover_document(
            cls,
            update: Union[PackageHandoverDocumentMediaUpdate, AssetHandoverDocumentMediaUpdate],
            handover_document_valid_statuses
    ) -> bool:
        return 'status' in update.old_data and \
               update.old_data['status'] not in handover_document_valid_statuses and \
               update.new_data['status'] in handover_document_valid_statuses
