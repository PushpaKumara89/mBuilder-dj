from unittest import mock
from unittest.mock import patch
from zipfile import ZipFile

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Exists, OuterRef, Q
from freezegun import freeze_time
from rest_framework.reverse import reverse

from api.models import AssetHandoverDocumentMedia, AssetHandoverDocumentMediaUpdate, HandoverDocument, \
    LocationMatrixPackage, AssetHandover, AssetHandoverDocument, PackageHandoverDocumentMedia, \
    PackageHandoverDocumentMediaUpdate, AssetHandoverDocumentType, PackageHandover, LocationMatrix, Media
from api.services.handover_document_service import HandoverDocumentService
from api.tests.test import TestCase, data_provider


class HandoverDocumentTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/handover_document.json',
    ]
    file_system_storage = FileSystemStorage()
    WORKING_PROJECT = 5

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/media/troom.png'

    def mock_archive_link(self, *args, **kwargs):
        return 'http://localhost/media/archive.zip'

    def get_filters_for_search_by_superuser(self):
        return (
            (
                {'all': 1, 'expand': [
                    'expanded_package',
                    'expanded_package_activity',
                    'expanded_company',
                    'expanded_media',
                    'expanded_document_type'
                ]},
                '/handover_document/get_all_by_superuser.json'
            ),
            (
                {'all': 1, 'search': '123'},
                '/handover_document/search_by_uid.json'
            ),
            (
                {'all': 1, 'search': 'broom'},
                '/handover_document/search_by_filename.json'
            ),
            (
                {'all': 1, 'search': 'media'},
                '/handover_document/search_by_information.json'
            ),
            (
                {'all': 1, 'building': ['Building A']},
                '/handover_document/filter_by_building.json'
            ),
            (
                {'all': 1, 'level': ['7A']},
                '/handover_document/filter_by_level.json'
            ),
            (
                {'all': 1, 'area': ['Hall']},
                '/handover_document/filter_by_area.json'
            ),
            (
                {'all': 1, 'package': [3]},
                '/handover_document/filter_by_package.json'
            ),
            (
                {'all': 1, 'package_activity': [5]},
                '/handover_document/filter_by_package_activity.json'
            ),
            (
                {'all': 1, 'company': [2]},
                '/handover_document/filter_by_company.json'
            ),
            (
                {'all': 1, 'asset_handover_document_type': [1]},
                '/handover_document/filter_by_document_type.json'
            ),
        )

    def get_filters_for_search_by_subcontractor(self):
        return (
            (
                {'all': 1},
                '/handover_document/get_all_by_subcontractor.json'
            ),
            (
                {'all': 1, 'search': 'sub'},
                '/handover_document/search_by_uid_by_subcontractor.json'
            ),
            (
                {'all': 1, 'search': 'broom'},
                '/handover_document/search_by_filename_by_subcontractor.json'
            ),
            (
                {'all': 1, 'search': 'bingo'},
                '/handover_document/search_by_information_by_subcontractor.json'
            ),
            (
                {'all': 1, 'building': ['Building A']},
                '/handover_document/filter_by_building_by_subcontractor.json'
            ),
            (
                {'all': 1, 'level': ['7A']},
                '/handover_document/filter_by_level_by_subcontractor.json'
            ),
            (
                {'all': 1, 'area': ['Hall']},
                '/handover_document/filter_by_area_by_subcontractor.json'
            ),
            (
                {'all': 1, 'package': [4]},
                '/handover_document/filter_by_package_by_subcontractor.json'
            ),
            (
                {'all': 1, 'package_activity': [5]},
                '/handover_document/filter_by_package_activity_by_subcontractor.json'
            ),
            (
                {'all': 1, 'asset_handover_document_type': [1]},
                '/handover_document/filter_by_document_type_by_subcontractor.json'
            ),
        )

    def get_filters_for_search_by_consultant(self):
        return (
            (
                {'all': 1},
                '/handover_document/get_all_by_consultant.json'
            ),
            (
                {'all': 1, 'search': 'sub'},
                '/handover_document/search_by_uid_by_consultant.json'
            ),
            (
                {'all': 1, 'search': 'broom'},
                '/handover_document/search_by_filename_by_consultant.json'
            ),
            (
                {'all': 1, 'search': 'bingo'},
                '/handover_document/search_by_information_by_consultant.json'
            ),
            (
                {'all': 1, 'building': ['Building A']},
                '/handover_document/filter_by_building_by_consultant.json'
            ),
            (
                {'all': 1, 'level': ['7A']},
                '/handover_document/filter_by_level_by_consultant.json'
            ),
            (
                {'all': 1, 'area': ['Hall']},
                '/handover_document/filter_by_area_by_consultant.json'
            ),
            (
                {'all': 1, 'package': [3]},
                '/handover_document/filter_by_package_by_consultant.json'
            ),
            (
                {'all': 1, 'package_activity': [5]},
                '/handover_document/filter_by_package_activity_by_consultant.json'
            ),
            (
                {'all': 1, 'asset_handover_document_type': [1]},
                '/handover_document/filter_by_document_type_by_consultant.json'
            ),
        )

    @data_provider(get_filters_for_search_by_superuser)
    def test_search(self, filters, fixture):
        url = reverse('handover_documents-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_search_by_consultant)
    def test_search_by_consultant(self, filters, fixture):
        url = reverse('handover_documents-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters_for_search_by_subcontractor)
    def test_search_by_subcontractor(self, filters, fixture):
        url = reverse('handover_documents-list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_retrieve(self):
        url = reverse('handover_documents-retrieve', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': 1})
        self._log_in_as_superuser()
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/handover_document/retrieve.json')

    def test_create_from_asset_handover_document_media(self):
        request_fixture = self.load_request_fixture('/handover_document/create_asset_handover_document_media.json')
        url = reverse('asset_handover_document_media_list', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_superuser()
        response = self.client.post(url, request_fixture)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'asset_handover_document': request_fixture['asset_handover_document'],
            'media': request_fixture['media'],
            'uid': request_fixture['uid']
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, {
            'asset_handover_document_media__asset_handover_document': request_fixture['asset_handover_document'],
            'asset_handover_document_media__media': request_fixture['media'],
            'comment': None,
        })

        document_media = AssetHandoverDocumentMedia.objects.select_related(
            'asset_handover_document__asset_handover__location_matrix__project'
        ).filter(asset_handover_document=request_fixture['asset_handover_document']).order_by('-id').first()
        asset_handover = document_media.asset_handover_document.asset_handover
        project = asset_handover.project
        package_activity = asset_handover.package_activity
        package = LocationMatrixPackage.objects.filter(
            location_matrix__project=project,
            location_matrix=document_media.asset_handover_document.asset_handover.location_matrix,
            package_activity=package_activity
        ).get().package
        last_update = AssetHandoverDocumentMediaUpdate.objects.filter(
            asset_handover_document_media=document_media
        ).order_by('-created_at').first()

        self.assertDatabaseHas(HandoverDocument, {
            'document_type': document_media.asset_handover_document.document_type.id,
            'building': asset_handover.location_matrix.building,
            'level': asset_handover.location_matrix.level,
            'area': asset_handover.location_matrix.area,
            'company': last_update.user.company,
            'filename': document_media.media.name,
            'media': document_media.media,
            'entity_id': document_media.id,
            'package': package,
            'package_activity': package_activity,
            'project': project,
            'uid': document_media.uid,
            'entity': HandoverDocument.Entities.ASSET_HANDOVER
        })

    def test_create_on_bulk_create_asset_handover_document_media_updates(self):
        updating_asset_handover_document = 2
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/handover_document/bulk_create_asset_handover_document_media_update.json')
        self._log_in_as_superuser()
        response = self.client.post(url, creation_data)

        self.assertCreated(response)
        self.assertSoftDeleted(AssetHandoverDocumentMedia, {
            'asset_handover_document': updating_asset_handover_document
        })

        deleted_document_media = AssetHandoverDocumentMedia.deleted_objects.filter(
            asset_handover_document=updating_asset_handover_document,
            status=AssetHandoverDocumentMedia.Status.REMOVED
        )
        # Check all document media changed status to the same.
        self.assertEquals(
            2,
            deleted_document_media.count()
        )

        document_media_ids = list(deleted_document_media.values_list('id', flat=True))

        self.assertSoftDeleted(HandoverDocument, {
            'entity': HandoverDocument.Entities.ASSET_HANDOVER,
            'entity_id__in': document_media_ids
        })

    def test_restore_on_bulk_create_asset_handover_document_media_updates(self):
        updating_asset_handover_document = 12
        restoring_handover_document = 6
        url = reverse('bulk_create_asset_handover_document_media_updates', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_asset_handover_document
        })
        creation_data = self.load_request_fixture('/handover_document/restore_on_bulk_create_asset_handover_document_media_update.json')
        self._log_in_as_superuser()
        response = self.client.post(url, creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(HandoverDocument, restoring_handover_document)

    def test_update_on_asset_handover_document_media_update(self):
        updating_asset_handover_document_media = 4
        url = reverse('asset_handover_document_media_update_list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'media_pk': updating_asset_handover_document_media
        })
        creation_data = self.load_request_fixture('/handover_document/create_asset_handover_document_media_update.json')
        self._log_in_as_superuser()
        response = self.client.post(url, creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(HandoverDocument, {
            'entity': HandoverDocument.Entities.ASSET_HANDOVER,
            'entity_id': updating_asset_handover_document_media,
            'filename': 'kroom.png',
            'uid': creation_data['new_data']['uid'],
            'media': creation_data['new_data']['media']
        })

    def test_delete_asset_handover(self):
        deleting_asset_handover = 1
        self._log_in_as_superuser()
        url = reverse('asset_handover_details', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': deleting_asset_handover})
        response = self.client.delete(url)

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, deleting_asset_handover)

        deleted_document_media = list(AssetHandoverDocumentMedia.objects.filter(
            asset_handover_document__asset_handover=deleting_asset_handover
        ).values_list('id', flat=True))

        self.assertSoftDeleted(HandoverDocument, {
            'entity': HandoverDocument.Entities.ASSET_HANDOVER,
            'entity_id__in': deleted_document_media
        })

    # Test with related asset handover information creation.
    @freeze_time("2021-11-11")
    def test_create_asset_handover_documents(self):
        data = self.load_request_fixture('/handover_document/create_asset_handover_document_for_multiple_locations.json')
        url = reverse('asset_handover_list', kwargs={'project_pk': self.WORKING_PROJECT})
        working_asset_handover = 7

        self._log_in_as_superuser()
        response = self.client.post(url, data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/handover_document/create_asset_handover_document_response_assertion.json')

        del data['asset_handover_information']

        # Check restored.
        self.assertDatabaseHas(AssetHandover, working_asset_handover)

        # Check that documents for restored asset handover were updated.
        self.assertDatabaseHas(AssetHandoverDocument, {
            'asset_handover': working_asset_handover,
            'document_type': AssetHandoverDocumentType.Types.ASBUILT_DRAWING.value,
            'number_required_files': 2
        })
        self.assertDatabaseHas(AssetHandoverDocument, {
            'asset_handover': working_asset_handover,
            'document_type': AssetHandoverDocumentType.Types.TEST_PACK.value,
            'number_required_files': 1
        })

        self.assertDatabaseHas(HandoverDocument, {
            'entity_id': 14,
            'entity': HandoverDocument.Entities.ASSET_HANDOVER
        })

    def test_create_from_package_handover_document_media(self):
        url = reverse('package_handover_document_media_list', kwargs={'project_pk': self.WORKING_PROJECT})
        superuser = self._get_superuser()
        new_package_handover_document_media = self.load_request_fixture('/handover_document/create_consultant_package_handover_document_media.json')

        self.force_login_user(superuser.pk)
        response = self.client.post(url, new_package_handover_document_media)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocumentMedia, new_package_handover_document_media)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'user': superuser.pk,
                'package_handover_document_media': response.data['id'],
                'new_data': {
                    'status': PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL.value,
                    'media': new_package_handover_document_media['media']
                }
            }
        )
        self.assertDatabaseHas(HandoverDocument, {
            'entity': HandoverDocument.Entities.PACKAGE_HANDOVER,
            'entity_id': response.data['id'],
            'uid': new_package_handover_document_media['uid'],
            'information': new_package_handover_document_media['information']
        })

    def test_remove_package_handover_document_media(self):
        working_package_handover_document_media = 2
        url = reverse(
            'package_handover_document_media_updates_list',
            kwargs={'project_pk': self.WORKING_PROJECT, 'media_pk': working_package_handover_document_media}
        )
        new_package_handover_document_media_update = self.load_request_fixture('/handover_document/remove_package_handover_document_media.json')
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': superuser.pk, 'package_handover_document_media': working_package_handover_document_media,
             **new_package_handover_document_media_update}
        )
        self.assertSoftDeleted(
            PackageHandoverDocumentMedia,
            {'pk': working_package_handover_document_media, **new_package_handover_document_media_update['new_data']}
        )

        self.assertSoftDeleted(HandoverDocument, {
            'entity': HandoverDocument.Entities.PACKAGE_HANDOVER,
            'entity_id': working_package_handover_document_media
        })

    def test_delete_on_location_matrix_change(self):
        payload = self.load_request_fixture('/handover_document/delete_on_location_matrix_change.json')
        deleted_package_handover = 4
        url = reverse('location_matrix_bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})

        self._log_in_as_staff(project=self.WORKING_PROJECT, editmode__project=self.WORKING_PROJECT)
        response = self.client.post(url, payload)

        self.assertOk(response)
        self.assertSoftDeleted(PackageHandover, deleted_package_handover)

        package_handover_document_media_ids = list(PackageHandoverDocumentMedia.objects.filter(
            package_handover_document__package_handover=deleted_package_handover
        ).values_list('id', flat=True))

        for package_handover_document_media in package_handover_document_media_ids:
            self.assertSoftDeleted(HandoverDocument, {
                'entity': HandoverDocument.Entities.PACKAGE_HANDOVER,
                'entity_id': package_handover_document_media
            })

    def test_update_on_package_handover_document_media_update(self):
        working_package_handover_document_media = 1
        url = reverse(
            'package_handover_document_media_updates_list',
            kwargs={'project_pk': self.WORKING_PROJECT, 'media_pk': working_package_handover_document_media}
        )
        new_package_handover_document_media_update = self.load_request_fixture('/handover_document/update_package_handover_document_media.json')
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': superuser.pk, 'package_handover_document_media': working_package_handover_document_media,
             **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': working_package_handover_document_media, **new_package_handover_document_media_update['new_data']}
        )

        self.assertSoftDeleted(HandoverDocument, {
            'entity': HandoverDocument.Entities.PACKAGE_HANDOVER,
            'entity_id': working_package_handover_document_media
        })

    def test_update_on_location_matrix_update(self):
        payload = self.load_request_fixture('/handover_document/update_location_matrix.json')
        updating_location_matrix = payload[0]
        url = reverse('location_matrix_bulk_create', kwargs={'project_pk': self.WORKING_PROJECT})

        self._log_in_as_staff(project=self.WORKING_PROJECT, editmode__project=self.WORKING_PROJECT)
        response = self.client.post(url, payload)

        self.assertOk(response)
        self.assertDatabaseHas(LocationMatrix, updating_location_matrix)

        asset_handover_document_media = list(AssetHandoverDocumentMedia.objects.filter(
            Exists(HandoverDocument.objects.filter(
                entity_id=OuterRef('id'),
                entity=HandoverDocument.Entities.ASSET_HANDOVER,
                deleted__isnull=True
            )),
            asset_handover_document__asset_handover__location_matrix_id=updating_location_matrix['id']
        ).values_list('id', flat=True))

        for document_media in asset_handover_document_media:
            self.assertDatabaseHas(HandoverDocument, {
                'entity_id': document_media,
                'entity': HandoverDocument.Entities.ASSET_HANDOVER,
                'building': updating_location_matrix['building'],
                'level': updating_location_matrix['level'],
                'area': updating_location_matrix['area'],
            })

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_retrieve_handover_document_single_media_by_superuser(self):
        url = reverse('handover_documents-media', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': 1})
        self._log_in_as_superuser()
        response = self.client.get(url)

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    def test_unauthorized_retrieve_handover_document_single_media(self):
        url = reverse('handover_documents-media', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': 1})
        response = self.client.get(url)

        self.assertUnauthorized(response)

    @patch('api.storages.AzurePrivateMediaStorage.url', mock_media_link)
    def test_retrieve_handover_document_single_media_by_project_user(self):
        url = reverse('handover_documents-media', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': 1})
        self._log_in_as_staff(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertRedirects(response, self.mock_media_link(), fetch_redirect_response=False)

    def test_retrieve_handover_document_single_media_by_non_project_user(self):
        url = reverse('handover_documents-media', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': 1})
        self._log_in_as_staff(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def mock_generated_archive_name(self):
        return 'archive.zip'

    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_archive_link)
    @patch('api.storages.AzurePrivateMediaStorage.save', file_system_storage.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', file_system_storage.open)
    @patch.object(HandoverDocumentService, '_HandoverDocumentService__generate_archive_name', mock_generated_archive_name)
    def test_download_multiple_handover_documents_by_superuser(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        superuser = self._get_superuser()
        handover_documents = [1, 5]
        url = reverse('handover_documents-media_batch', kwargs={'project_pk': self.WORKING_PROJECT})

        self.force_login_user(superuser.pk)
        response = self.client.post(url, {'handover_document': handover_documents})

        self.assertOk(response)
        self.assertDatabaseHas(Media, {'name': 'archive.zip'})

        with ZipFile('media/archive.zip', 'r') as zip_archive:
            media_names = list(Media.objects.filter(handoverdocument__id__in=handover_documents).values_list('name', flat=True))
            files_namelist = zip_archive.namelist()
            for media_name in media_names:
                self.assertIn(media_name, files_namelist)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information Report - Archive of selected files',
                'to': [superuser.email],
                'from_email': 'MBuild Support <some_email@email.com>',
                'fixture': self.responses_fixtures_dir + '/handover_document/notify_about_ability_to_download_archive_with_handover_documents.html'
            }
        ])

    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_archive_link)
    @patch('api.storages.AzurePrivateMediaStorage.save', file_system_storage.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', file_system_storage.open)
    @patch.object(HandoverDocumentService, '_HandoverDocumentService__generate_archive_name', mock_generated_archive_name)
    def test_download_multiple_handover_documents_by_project_user(self):
        self.generate_and_save_fake_image('troom.png')
        self.generate_and_save_fake_image('broom.png')

        staff = self._get_staff(project=self.WORKING_PROJECT)
        handover_documents = [1, 5]
        url = reverse('handover_documents-media_batch', kwargs={'project_pk': self.WORKING_PROJECT})

        self.force_login_user(staff.pk)
        response = self.client.post(url, {'handover_document': handover_documents})

        self.assertOk(response)
        self.assertDatabaseHas(Media, {'name': 'archive.zip'})

        with ZipFile('media/archive.zip', 'r') as zip_archive:
            media_names = list(Media.objects.filter(handoverdocument__id__in=handover_documents).values_list('name', flat=True))
            files_namelist = zip_archive.namelist()
            for media_name in media_names:
                self.assertIn(media_name, files_namelist)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information Report - Archive of selected files',
                'to': [staff.email],
                'from_email': 'MBuild Support <some_email@email.com>',
                'fixture': self.responses_fixtures_dir + '/handover_document/notify_about_ability_to_download_archive_with_handover_documents.html'
            }
        ])

    def test_download_multiple_handover_documents_by_non_project_user(self):
        non_project_staff = self._get_staff(~Q(project=self.WORKING_PROJECT))
        handover_documents = [1, 5]
        url = reverse('handover_documents-media_batch', kwargs={'project_pk': self.WORKING_PROJECT})

        self.force_login_user(non_project_staff.pk)
        response = self.client.post(url, {'handover_document': handover_documents})

        self.assertForbidden(response)

    def test_unauthorized_download_multiple_handover_documents(self):
        handover_documents = [1, 5]
        url = reverse('handover_documents-media_batch', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.post(url, {'handover_document': handover_documents})

        self.assertUnauthorized(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_superuser(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_superuser()
        response = self.client.get(url)

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/handover_document/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_admin(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad+2wood@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/handover_document/csv_report_created_by_project_admin.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_manager(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad+1@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/handover_document/csv_report_created_by_project_manager.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_subcontractor(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.subcontractor@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/handover_document/csv_report_created_by_project_subcontractor.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_consultant(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['wrap.trap1@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/handover_document/csv_report_created_by_project_consultant.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', file_system_storage.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_media_link)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_client(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Handover Information CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.client@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/handover_document/csv_report_created_by_project_client.html'
            }
        ])

    def test_forbid_get_csv_by_non_project_admin(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_forbid_get_csv_by_non_project_manager(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_forbid_get_csv_by_non_project_subcontractor(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_forbid_get_csv_by_non_project_consultant(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_forbid_get_csv_by_non_project_client(self):
        url = reverse('handover_documents-generate_csv', kwargs={'project_pk': self.WORKING_PROJECT})
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_delete_on_package_handover_document_delete(self):
        deleting_document = 1
        url = reverse('package_handover_documents_detail', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': deleting_document})
        self._log_in_as_superuser()
        response = self.client.delete(url)

        self.assertNoContent(response)

        package_handover_document_media = list(PackageHandoverDocumentMedia.objects.filter(
            package_handover_document=deleting_document
        ).values_list('id', flat=True))

        self.assertSoftDeleted(HandoverDocument, {
            'entity': HandoverDocument.Entities.PACKAGE_HANDOVER,
            'entity_id__in': package_handover_document_media
        })
