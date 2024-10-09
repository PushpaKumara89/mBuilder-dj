import dataclasses
import datetime
import os
import time
import uuid
from abc import abstractmethod
from typing import Literal, Optional
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

from azure.storage.blob import BlobClient, ContentSettings, generate_blob_sas, BlobSasPermissions
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Subquery, OuterRef
from sentry_sdk import capture_exception
from requests.exceptions import ConnectionError

from api.mails.handover_document.download_handover_archive import DownloadHandoverArchive
from api.models import User, Project, HandoverDocumentArchive, AssetHandoverDocumentMedia, PackageMatrix, Media, \
    PackageHandoverDocumentMedia, PackageHandoverDocumentType, HandoverDocumentArchivePart
from api.queues.celery.handover_document_archive import generate_archive_part
from api.services.handover_document_archive_entity_service import HandoverDocumentArchiveEntityService
from api.services.handover_document_archive_part_entity_service import HandoverDocumentArchivePartEntityService
from api.services.media_entity_service import MediaEntityService
from api.storages import AzurePrivateMediaStorage
from api.utilities.handover_document_utilities import extend_file_name_for_archive, replace_forward_slash_by_dash
from api.utilities.report_generators.handover_document_archive_report_generator import \
    HandoverDocumentArchiveReportGenerator
from mbuild.settings import AZURE_BLOB_CONNECTION_STRING, AZURE_PRIVATE_MEDIA_CONTAINER, AZURE_ACCOUNT_NAME, \
    AZURE_ACCOUNT_KEY, HANDOVER_DOCUMENT_ARCHIVE_EXPIRATION_IN_DAYS, HANDOVER_DOCUMENT_ARCHIVE_TEMP_FILE_FOLDER


class ArchivePartStrGenerator:
    date: str
    project_name: str
    total_archive_parts_count: int
    current_archive_parts_number: int
    starting_files_number: int
    ending_files_number: int

    def __init__(self, archive_part: HandoverDocumentArchivePart):
        self.date = self.get_date(archive_part)
        self.project_name = self.get_project_name(archive_part)
        self.total_archive_parts_count = archive_part.handover_document_archive.handoverdocumentarchivepart_set.count()
        self.current_archive_parts_number = archive_part.handover_document_archive.handoverdocumentarchivepart_set.filter(
            id__lte=archive_part.id
        ).count()
        in_range_files_counts = archive_part.handover_document_archive.handoverdocumentarchivepart_set.filter(
            id__lt=archive_part.id
        ).values_list('in_range_files_count', flat=True)
        self.starting_files_number = sum(in_range_files_counts)
        self.ending_files_number = self.starting_files_number + archive_part.in_range_files_count

    @abstractmethod
    def get_project_name(self, archive_part: HandoverDocumentArchivePart) -> str:
        pass

    @abstractmethod
    def get_date(self, archive_part: HandoverDocumentArchivePart) -> str:
        pass


class ArchiveNameGenerator(ArchivePartStrGenerator):
    def get_date(self, archive_part: HandoverDocumentArchivePart) -> str:
        return archive_part.handover_document_archive.generation_started_at.strftime('%Y-%m-%d_%H-%M-%S')

    def get_project_name(self, archive_part: HandoverDocumentArchivePart) -> str:
        return archive_part.handover_document_archive.project.name.replace(' ', '_')

    def __str__(self):
        return ('%s_%s_of_%s_%s_%s_%s.zip'
                % (self.project_name, self.current_archive_parts_number, self.total_archive_parts_count,
                   self.date, self.starting_files_number + 1, self.ending_files_number))


class EmailSubjectGenerator(ArchivePartStrGenerator):
    total_files_count: int

    def __init__(self, archive_part: HandoverDocumentArchivePart):
        super().__init__(archive_part)

        self.total_files_count = archive_part.total_files_count

    def get_project_name(self, archive_part: HandoverDocumentArchivePart) -> str:
        return archive_part.handover_document_archive.project.name

    def get_date(self, archive_part: HandoverDocumentArchivePart) -> str:
        return archive_part.handover_document_archive.generation_started_at.strftime('%d/%m/%Y')

    def __str__(self):
        return ('MBuild - Handover Archive: (%s of %s expected): %s - %s - Files %s - %s of %s'
                % (self.current_archive_parts_number, self.total_archive_parts_count, self.project_name,
                   self.date, self.starting_files_number + 1, self.ending_files_number, self.total_files_count))


@dataclasses.dataclass()
class BaseHandoverArchiveGroup:
    def to_dir_tree(self):
        path_parts = [getattr(self, folder.name) for folder in dataclasses.fields(self)]

        return '/'.join([part for part in path_parts if part is not None])


@dataclasses.dataclass(unsafe_hash=True)
class AssetHandoverArchiveGroup(BaseHandoverArchiveGroup):
    entity: str
    package: str
    package_activity: str
    building: str
    level: str
    area: str
    type: str

    def __init__(self, asset_handover_document_media: AssetHandoverDocumentMedia):
        self.entity = 'Asset Handover'
        self.package = replace_forward_slash_by_dash(asset_handover_document_media.package)
        self.package_activity = replace_forward_slash_by_dash(
            asset_handover_document_media.asset_handover_document.asset_handover.package_activity.name)
        self.building = replace_forward_slash_by_dash(
            asset_handover_document_media.asset_handover_document.asset_handover.location_matrix.building)
        self.level = replace_forward_slash_by_dash(
            asset_handover_document_media.asset_handover_document.asset_handover.location_matrix.level)
        self.area = replace_forward_slash_by_dash(
            asset_handover_document_media.asset_handover_document.asset_handover.location_matrix.area)
        self.type = replace_forward_slash_by_dash(
            asset_handover_document_media.asset_handover_document.document_type.name)


@dataclasses.dataclass(unsafe_hash=True)
class PackageHandoverArchiveGroup(BaseHandoverArchiveGroup):
    entity: str
    package: str
    package_activity: str
    document_group: str

    _document_type: str
    _information: Optional[str]

    @property
    def document_type(self) -> str:
        return self._document_type

    @document_type.setter
    def document_type(self, document_type: PackageHandoverDocumentType) -> None:
        self._document_type = replace_forward_slash_by_dash(f'{document_type.id}. {document_type.name}')

    @property
    def information(self) -> str:
        return self._information

    @information.setter
    def information(self, information: Optional[str]) -> None:
        if type(information) is str:
            information = replace_forward_slash_by_dash(''.join(information.strip().splitlines()))
            if len(information) > 255:
                information = information[:255]

        self._information = information

    def __init__(self, package_handover_document_media: PackageHandoverDocumentMedia):
        self.entity = 'Package Handover'
        self.package = replace_forward_slash_by_dash(
            package_handover_document_media.package_handover_document.package_handover.package_matrix.package.name)
        self.package_activity = replace_forward_slash_by_dash(
            package_handover_document_media.package_handover_document.package_handover.package_matrix.package_activity.name)
        self.document_group = replace_forward_slash_by_dash(
            package_handover_document_media.package_handover_document.package_handover_document_type.group.name)
        self.document_type = (package_handover_document_media.package_handover_document
                              .package_handover_document_type)
        self.information = package_handover_document_media.information


@dataclasses.dataclass
class ArchivePartBoundaries:
    size: float = 0
    files_count: int = 0
    asset_handover_limit: int = 0
    asset_handover_offset: int = 0
    package_handover_limit: int = 0
    package_handover_offset: int = 0


class HandoverDocumentArchiveService:
    def initiate_generation_process(self, project: int, user: User, generation_started_at: datetime.datetime) -> None:
        project = Project.objects.filter(id=project).first()

        if not project:
            return

        if self._is_incomplete_generation_exists(user, project):
            return

        handover_document_archive: HandoverDocumentArchive = HandoverDocumentArchiveEntityService().create({
            'user': user, 'project': project, 'generation_started_at': generation_started_at
        })

        parts_boundaries: list[ArchivePartBoundaries] = []
        asset_handover_files_count = self._get_asset_handover_media_boundaries(project, parts_boundaries)
        package_handover_files_count = self._get_package_handover_media_boundaries(project, parts_boundaries)

        total_files_count = asset_handover_files_count + package_handover_files_count

        # We have to be sure all archive parts created before starting archive generation.
        with transaction.atomic():
            for part_boundaries in parts_boundaries:
                data = {
                    'handover_document_archive_id': handover_document_archive.id,
                    'asset_handover_media_range': {
                        'limit': part_boundaries.asset_handover_limit,
                        'offset': part_boundaries.asset_handover_offset
                    },
                    'package_handover_media_range': {
                        'limit': part_boundaries.package_handover_limit,
                        'offset': part_boundaries.package_handover_offset
                    },
                    'in_range_files_count': part_boundaries.asset_handover_limit + part_boundaries.package_handover_limit,
                    'total_files_count': total_files_count
                }
                HandoverDocumentArchivePartEntityService().create(data)

        self._start_archive_generation(handover_document_archive)

    def _start_archive_generation(self, archive: HandoverDocumentArchive) -> None:
        archive_part = archive.handoverdocumentarchivepart_set.order_by('id').first()
        if archive_part:
            self.create_archive_part_file(archive_part)
        else:
            HandoverDocumentArchiveEntityService().set_status_to_completed(archive)

    def send_archive_part(self, archive_part: HandoverDocumentArchivePart) -> None:
        archive_media = archive_part.media

        (DownloadHandoverArchive()
         .set_context({
            'archive_url': self._get_sas_url(archive_media),
            'archive_size': archive_media.size,
            'files_count': archive_part.in_range_files_count,
            'email': settings.EMAIL_COMPLETIONS_EMAIL,
         })
         .set_subject(str(EmailSubjectGenerator(archive_part)))
         .set_to(archive_part.handover_document_archive.user.email)
         .send())

        HandoverDocumentArchivePartEntityService().set_status_to_sent(archive_part)

    def process_next_part(self, archive_part: HandoverDocumentArchivePart) -> None:
        next_part = HandoverDocumentArchivePart.objects.filter(
            handover_document_archive_id=archive_part.handover_document_archive.id,
            id__gt=archive_part.id
        ).select_related(
            'handover_document_archive__project', 'handover_document_archive__user'
        ).order_by('id').first()

        if next_part:
            generate_archive_part.delay(next_part)
        else:
            HandoverDocumentArchiveEntityService().set_status_to_completed(archive_part.handover_document_archive)

    def create_archive_part_file(self, archive_part: HandoverDocumentArchivePart) -> Optional[HandoverDocumentArchivePart]:
        archive_part_service = HandoverDocumentArchivePartEntityService()

        try:
            zip_file_name = self._create_temporary_file(archive_part, archive_part_service)
            media = self._save_file(archive_part, zip_file_name)
            archive_part = self._set_archive_part_media(archive_part, media)

            archive_part_service.set_status_to_saved(archive_part)

            self.send_archive_part(archive_part)
            self.process_next_part(archive_part)
        except Exception as e:
            event_id = capture_exception(e)
            archive_part_service.mark_as_failed(archive_part, event_id)

    def _create_temporary_file(self, archive_part: HandoverDocumentArchivePart,
                               archive_part_service: HandoverDocumentArchivePartEntityService) -> str:
        archive_part_service.set_status_to_running(archive_part)

        project = archive_part.handover_document_archive.project
        asset_handover_archive_data, asset_handover_files_count = self._get_asset_handover_archive_data(
            project, archive_part
        )
        package_handover_archive_data, package_handover_files_count = self._get_package_handover_archive_data(
            project, archive_part
        )
        zip_file_name = self._get_temporary_zipfile_name()

        with ZipFile(zip_file_name, 'w', compression=ZIP_DEFLATED) as archive:
            self._archive_document_media(archive, asset_handover_archive_data)
            self._archive_document_media(archive, package_handover_archive_data)

            is_first_part = not archive_part.handover_document_archive.handoverdocumentarchivepart_set.filter(
                id__lt=archive_part.id
            ).exists()

            if is_first_part:
                self._archive_csv_report(archive, project)

        return zip_file_name

    def _get_sas_url(self, media: Media) -> str:
        blob_url = BlobClient.from_connection_string(
            conn_str=AZURE_BLOB_CONNECTION_STRING,
            container_name=AZURE_PRIVATE_MEDIA_CONTAINER,
            blob_name=media.name
        ).url
        sas_token = generate_blob_sas(
            account_name=AZURE_ACCOUNT_NAME,
            account_key=AZURE_ACCOUNT_KEY,
            container_name=AZURE_PRIVATE_MEDIA_CONTAINER,
            permission=BlobSasPermissions(read=True),
            blob_name=media.name,
            start=datetime.datetime.now(),
            expiry=datetime.datetime.now() + datetime.timedelta(days=HANDOVER_DOCUMENT_ARCHIVE_EXPIRATION_IN_DAYS)
        )

        return f'{blob_url}?{sas_token}'

    def _is_incomplete_generation_exists(self, user: User, project: Project) -> bool:
        return HandoverDocumentArchive.objects.filter(
            ~Q(status=HandoverDocumentArchive.Status.COMPLETED),
            user=user, project=project
        ).exists()

    def _get_asset_handover_media_boundaries(self, project: Project,
                                             parts_boundaries: list[ArchivePartBoundaries]) -> int:
        asset_handovers_media = (
            AssetHandoverDocumentMedia.objects.filter_for_handover_document_archive(project).select_related('media')
        )

        self._collect_boundaries(parts_boundaries, asset_handovers_media, 'asset_handover')

        return asset_handovers_media.count()

    def _get_package_handover_media_boundaries(self, project: Project,
                                               parts_boundaries: list[ArchivePartBoundaries]) -> int:
        package_handovers_media = (
            PackageHandoverDocumentMedia.objects.filter_for_handover_document_archive(project)
            .select_related('media')
        )

        self._collect_boundaries(parts_boundaries, package_handovers_media, 'package_handover')

        return package_handovers_media.count()

    def _collect_boundaries(self, archive_parts_boundaries: list[ArchivePartBoundaries], handovers_media,
                            entity: Literal['asset_handover', 'package_handover']) -> None:
        summarized_size = archive_parts_boundaries[-1].size if archive_parts_boundaries else 0
        files_count = 0
        offset = 0

        if archive_parts_boundaries and archive_parts_boundaries[-1].size < settings.HANDOVER_DOCUMENT_ARCHIVE_PART_SIZE_IN_GB:
            current_part_boundaries = archive_parts_boundaries.pop()
        else:
            current_part_boundaries = ArchivePartBoundaries()

        for handover_media in handovers_media:
            files_count += 1
            summarized_size += round(handover_media.media.size / 1024 / 1024 / 1024, 5)

            if summarized_size >= settings.HANDOVER_DOCUMENT_ARCHIVE_PART_SIZE_IN_GB:
                self._collect_parts_boundaries(entity, current_part_boundaries, files_count, summarized_size,
                                               archive_parts_boundaries, offset)
                offset += files_count
                summarized_size = 0
                files_count = 0
                current_part_boundaries = ArchivePartBoundaries()

        if summarized_size:
            self._collect_parts_boundaries(entity, current_part_boundaries, files_count, summarized_size,
                                           archive_parts_boundaries, offset)

    def _collect_parts_boundaries(self, entity: Literal['asset_handover', 'package_handover'],
                                  current_part_boundaries: ArchivePartBoundaries, files_count: int,
                                  summarized_size: float, archive_parts_boundaries: list[ArchivePartBoundaries],
                                  current_file_number: int):
        self._set_limit_offset(entity, current_part_boundaries, files_count, current_file_number)

        current_part_boundaries.size = summarized_size
        current_part_boundaries.files_count = files_count
        archive_parts_boundaries.append(current_part_boundaries)

    def _set_limit_offset(self, entity: Literal['asset_handover', 'package_handover'],
                          current_part_boundaries: ArchivePartBoundaries, files_count: int,
                          current_file_number: int) -> None:
        if entity == 'asset_handover':
            current_part_boundaries.asset_handover_offset = current_file_number
            current_part_boundaries.asset_handover_limit = files_count
        elif entity == 'package_handover':
            current_part_boundaries.package_handover_offset = current_file_number
            current_part_boundaries.package_handover_limit = files_count

    def _set_archive_part_media(
            self, archive_part: HandoverDocumentArchivePart, media: Media
    ) -> HandoverDocumentArchivePart:
        archive_part.media = media
        archive_part.save(update_fields=['media'])
        archive_part.refresh_from_db()

        return archive_part

    def _get_temporary_zipfile_name(self) -> str:
        process_salt = str(uuid.uuid4())
        return f'{HANDOVER_DOCUMENT_ARCHIVE_TEMP_FILE_FOLDER}handover_document_archive_{process_salt}.zip'

    def _archive_document_media(self, archive: ZipFile, archive_data: dict) -> None:
        for group, media_list in archive_data.items():
            for handover_document_media in media_list:
                storage = handover_document_media.media.get_common_storage()
                file_data = self.load_file_data(storage, handover_document_media).read()
                file_path = self._get_file_path(archive, group, handover_document_media)
                creation_time = datetime.datetime.now().timetuple()[:6]
                archiving_file = ZipInfo(file_path, date_time=creation_time)
                archiving_file.compress_type = ZIP_DEFLATED

                archive.writestr(archiving_file, file_data)

    def load_file_data(self, storage, handover_document_media):
        attempt = 1
        retry_limit = 3
        attempt_sleeping_times = {
            1: 60,
            2: 300,
            3: 600
        }

        while attempt <= retry_limit:
            try:
                return storage.open(handover_document_media.media.name)
            except ConnectionError:
                if attempt == retry_limit:
                    raise

                time.sleep(attempt_sleeping_times.get(attempt, 60))
                attempt += 1

    def _get_file_path(self, archive: ZipFile, group, handover_document_media) -> str:
        file_path = group.to_dir_tree() + f'/{handover_document_media.media.name}'
        if file_path in archive.namelist():
            file_path = extend_file_name_for_archive(file_path)

        return file_path

    def _archive_csv_report(self, archive: ZipFile, project: Project) -> None:
        csv_content, csv_file_name = HandoverDocumentArchiveReportGenerator(
            project=project,
        ).generate_csv()
        creation_time = datetime.datetime.now().timetuple()[:6]
        archiving_file = ZipInfo(csv_file_name)

        archiving_file.compress_type = ZIP_DEFLATED
        archiving_file.date_time = creation_time

        archive.writestr(archiving_file, csv_content)

    def _save_file(self, archive_part: HandoverDocumentArchivePart, zip_file_name: str) -> Media:
        archive_name = self._get_archive_name(archive_part)
        file_size = os.path.getsize(zip_file_name)
        connection = BlobClient.from_connection_string(
            conn_str=AZURE_BLOB_CONNECTION_STRING,
            container_name=AzurePrivateMediaStorage.azure_container,
            blob_name=archive_name,
        )

        if not connection.exists():
            connection.create_append_blob(content_settings=ContentSettings(content_type='application/zip'))

        for content in self._gen_content_chunks(zip_file_name):
            connection.append_block(content, len(content))

        url = connection.url
        self._remove_temporary_file(zip_file_name)

        return MediaEntityService().create_media(
            is_public=False,
            rout_name='report_private_retrieve',
            original_link=url,
            file_name=archive_name,
            validated_data={},
            size=file_size
        )

    def _remove_temporary_file(self, zip_file_name: str) -> None:
        if os.path.exists(zip_file_name):
            os.remove(zip_file_name)

    def _gen_content_chunks(self, archive_file_path: str) -> bytes:
        # Maximum block length 4Mb
        archive_append_block_size = 4 * 1000 * 1000

        with open(archive_file_path, 'rb') as file:
            while True:
                data = file.read(archive_append_block_size)

                if data == b'':
                    break

                yield data

    def _get_asset_handover_archive_data(
            self, project: Project, archive_part: HandoverDocumentArchivePart
    ) -> tuple[dict, int]:
        asset_handover_archive_data = {}
        asset_handovers_media = (
            AssetHandoverDocumentMedia.objects.filter_for_handover_document_archive(project).annotate(
                package=Subquery(
                    PackageMatrix.all_objects.filter(
                        package_activity=OuterRef('asset_handover_document__asset_handover__package_activity_id'),
                        project=OuterRef('asset_handover_document__asset_handover__project_id')
                    ).select_related('package').values('package__name')[:1]
                )
            ).select_related(
                'media',
                'asset_handover_document__document_type',
                'asset_handover_document',
                'asset_handover_document__asset_handover__location_matrix',
                'asset_handover_document__asset_handover__package_activity'
            ).order_by('id')
        )
        asset_handovers_media = asset_handovers_media[archive_part.asset_handover_media_range['offset']
                                                      :archive_part.asset_handover_media_range['offset']
                                                       + archive_part.asset_handover_media_range['limit']]

        self._group_handover_documents(asset_handovers_media, asset_handover_archive_data,
                                       AssetHandoverArchiveGroup)

        return asset_handover_archive_data, len(asset_handovers_media)

    def _get_package_handover_archive_data(
            self, project: Project, archive_part: HandoverDocumentArchivePart
    ) -> tuple[dict, int]:
        package_handover_archive_data = {}
        package_handovers_media = (
            PackageHandoverDocumentMedia.objects.filter_for_handover_document_archive(project)
            .select_related(
                'media',
                'package_handover_document__project',
                'package_handover_document__package_handover__package_matrix__package',
                'package_handover_document__package_handover__package_matrix__package_activity',
                'package_handover_document__package_handover_document_type__group'
            ).order_by('id')
        )
        package_handovers_media = package_handovers_media[archive_part.package_handover_media_range['offset']
                                                          :archive_part.package_handover_media_range['offset']
                                                           + archive_part.package_handover_media_range['limit']]

        self._group_handover_documents(package_handovers_media, package_handover_archive_data,
                                       PackageHandoverArchiveGroup)

        return package_handover_archive_data, len(package_handovers_media)

    def _group_handover_documents(
            self, handovers_media: list, handover_archive_data: dict, archive_group_class
    ) -> None:
        for package_handover_media in handovers_media:
            group_key = archive_group_class(package_handover_media)
            if group_key not in handover_archive_data:
                handover_archive_data[group_key] = []

            handover_archive_data[group_key].append(package_handover_media)

    def _get_archive_name(self, archive_part: HandoverDocumentArchivePart) -> str:
        return str(ArchiveNameGenerator(archive_part))
