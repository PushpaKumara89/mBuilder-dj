from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from freezegun import freeze_time

from api.models import AssetHandoverDocument, User, AssetHandoverInformation
from api.models.asset_handover import AssetHandover
from api.tests.test import TestCase, data_provider


class AssetHandoverTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/asset_handovers.json',
    ]
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def get_filters_for_search(self):
        return (
            (
                {'limit': 2, 'offset': 3, 'sort': 'location_matrix', 'use_limit_offset_pagination': True},
                '/asset_handover/get_all.json'
            ),
            (
                {'company': [8]},
                '/asset_handover/filter_by_company.json'
            ),
        )

    @data_provider(get_filters_for_search)
    def test_search(self, filters, fixture):
        user = self._get_staff(project=5)
        self.force_login_user(user.pk)
        response = self.client.get('/api/projects/5/asset-handovers/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_delete_and_restore_on_location_matrix_package_change(self):
        project_staff = self._get_staff(project=5, editmode__project=5)
        sync_data = self.load_request_fixture('/asset_handover/delete_and_restore_on_location_matrix_package_change.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/projects/5/location-matrix-packages/sync/', sync_data)

        self.assertOk(response)
        self.assertSoftDeleted(AssetHandover, 8)

    @freeze_time('2023-01-01')
    def test_delete_and_restore_on_location_matrix_change(self):
        payload = self.load_request_fixture('/asset_handover/delete_and_restore_on_location_matrix_change.json')
        project_staff_in_edit_mode = self._get_staff(project=5, editmode__project=5)

        self.force_login_user(project_staff_in_edit_mode.pk)
        response = self.client.post('/api/projects/5/location-matrix/sync/', payload)

        self.assertOk(response)
        # Check that entity was deleted.
        self.assertSoftDeleted(AssetHandover, 1)
        # Check that entity was restored.
        self.assertDatabaseHas(AssetHandover, 3)

    def get_grouped_filters(self):
        return (
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True,
                 'expand': ['expanded_asset_handover_documents.expanded_asset_handover_document_media',
                            'expanded_asset_handover_documents.expanded_document_type']},
                '/asset_handover/get_grouped_by_superuser.json',
                {'is_superuser': True}
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True,
                 'expand': ['expanded_asset_handover_documents.expanded_asset_handover_document_media',
                            'expanded_asset_handover_documents.expanded_document_type']},
                '/asset_handover/get_grouped_by_company_admin.json',
                {'groups': User.Group.COMPANY_ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True,
                 'expand': ['expanded_asset_handover_documents.expanded_asset_handover_document_media',
                            'expanded_asset_handover_documents.expanded_document_type']},
                '/asset_handover/get_grouped_by_admin.json',
                {'groups': User.Group.ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True,
                 'expand': ['expanded_asset_handover_documents.expanded_asset_handover_document_media',
                            'expanded_asset_handover_documents.expanded_document_type']},
                '/asset_handover/get_grouped_by_manager.json',
                {'groups': User.Group.MANAGER.value}
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True,
                 'expand': ['expanded_asset_handover_documents.expanded_asset_handover_document_media',
                            'expanded_asset_handover_documents.expanded_document_type']},
                '/asset_handover/get_grouped_by_subcontractor.json',
                {'groups': User.Group.SUBCONTRACTOR.value, 'project': 5}
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True,
                 'expand': ['expanded_asset_handover_documents.expanded_asset_handover_document_media',
                            'expanded_asset_handover_documents.expanded_document_type']},
                '/asset_handover/get_grouped_by_client_.json',
                {'groups': User.Group.CLIENT.value, 'project': 5}
            ),
            (
                {'all': True, 'sort': 'id', 'use_limit_offset_pagination': True,
                 'expand': ['expanded_asset_handover_documents.expanded_asset_handover_document_media',
                            'expanded_asset_handover_documents.expanded_document_type']},
                '/asset_handover/get_grouped_by_consultant_.json',
                {'groups': User.Group.CONSULTANT.value, 'project': 5}
            ),
        )

    @data_provider(get_grouped_filters)
    def test_search_grouped(self, filters, fixture, user_filters):
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.get('/api/projects/5/asset-handovers/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_with_expanded(self):
        self.force_login_user(self._get_superuser().pk)
        response = self.client.get('/api/projects/5/asset-handovers/', {'expand': [
            'expanded_asset_handover_documents.expanded_document_type',
            'expanded_asset_handover_information',
            'expanded_asset_handover_documents.expanded_asset_handover_document_media.expanded_upload_update.expanded_user.expanded_user_company',
            'expanded_asset_handover_documents.expanded_asset_handover_document_media.expanded_last_status_change_update',
            'expanded_location_matrix'
        ], 'sort': 'id', 'use_limit_offset_pagination': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover/get_with_expanded.json')

    def test_unauthorized_search_grouped(self):
        response = self.client.get('/api/projects/5/asset-handovers/', {'all': True})

        self.assertUnauthorized(response)

    # Test with related asset handover information creation.
    @freeze_time("2021-11-11")
    def test_create_by_company_admin(self):
        data = self.load_request_fixture('/asset_handover/create_asset_handover_document_for_multiple_locations.json')
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.post('/api/projects/5/asset-handovers/', data)

        self.assertCreated(response)
        self.assertEqualsFixture(response.data, '/asset_handover/create_asset_handover_document_response_assertion.json')

        asset_handover_information = data.pop('asset_handover_information')
        self.assertDatabaseHas(AssetHandoverInformation, asset_handover_information)

        # Check restored.
        self.assertDatabaseHas(AssetHandover, 10)

        new_asset_handovers_number = AssetHandover.objects.filter(
            location_matrix__building=data['building'],
            package_activity=data['package_activity'],
            created_at='2021-11-11 00:00:00'
        ).count()
        self.assertEquals(new_asset_handovers_number, 1)

        document_number_created_for_type_one = AssetHandoverDocument.objects.filter(
            asset_handover__location_matrix__building=data['building'],
            number_required_files=2,
            document_type=1,
            asset_handover__package_activity=data['package_activity'],
            asset_handover__created_at='2021-11-11 00:00:00'
        ).count()
        self.assertEquals(document_number_created_for_type_one, 1)

        document_number_created_for_type_two = AssetHandoverDocument.objects.filter(
            asset_handover__location_matrix__building=data['building'],
            number_required_files=2,
            document_type=1,
            asset_handover__package_activity=data['package_activity'],
            asset_handover__created_at='2021-11-11 00:00:00'
        ).count()
        self.assertEquals(document_number_created_for_type_two, 1)

        # Check that documents for restored asset handover were updated.
        self.assertDatabaseHas(AssetHandoverDocument, {
            'asset_handover': 10,
            'document_type': 1,
            'number_required_files': 2
        })
        self.assertDatabaseHas(AssetHandoverDocument, {
            'asset_handover': 10,
            'document_type': 2,
            'number_required_files': 1
        })

    @freeze_time("2021-11-11")
    def test_create_by_admin(self):
        data = self.load_request_fixture('/asset_handover/create_asset_handover_document.json')
        self.force_login_user(self._get_admin().pk)
        response = self.client.post('/api/projects/5/asset-handovers/', data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocument, {
            'asset_handover__location_matrix__building': data['building'],
            'asset_handover__location_matrix__level': data['level'],
            'asset_handover__location_matrix__area': data['area'],
            'asset_handover__package_activity': data['package_activity'],
            'document_type': 1,
            'number_required_files': 2
        })
        self.assertDatabaseHas(AssetHandoverDocument, {
            'asset_handover__location_matrix__building': data['building'],
            'asset_handover__location_matrix__level': data['level'],
            'asset_handover__location_matrix__area': data['area'],
            'asset_handover__package_activity': data['package_activity'],
            'document_type': 2,
            'number_required_files': 1
        })

    @freeze_time("2021-11-11")
    def test_create_by_manager(self):
        data = self.load_request_fixture('/asset_handover/create_asset_handover_document.json')
        self.force_login_user(self._get_manager().pk)
        response = self.client.post('/api/projects/5/asset-handovers/', data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocument, {
            'asset_handover__location_matrix__building': data['building'],
            'asset_handover__location_matrix__level': data['level'],
            'asset_handover__location_matrix__area': data['area'],
            'asset_handover__package_activity': data['package_activity'],
            'document_type': 1,
            'number_required_files': 2
        })
        self.assertDatabaseHas(AssetHandoverDocument, {
            'asset_handover__location_matrix__building': data['building'],
            'asset_handover__location_matrix__level': data['level'],
            'asset_handover__location_matrix__area': data['area'],
            'asset_handover__package_activity': data['package_activity'],
            'document_type': 2,
            'number_required_files': 1
        })

    def test_forbid_create_by_client(self):
        data = self.load_request_fixture('/asset_handover/create_asset_handover_document.json')
        self.force_login_user(self._get_client().pk)
        response = self.client.post('/api/projects/5/asset-handovers/', data)

        self.assertForbidden(response)

    def test_forbid_create_by_consultant(self):
        data = self.load_request_fixture('/asset_handover/create_asset_handover_document.json')
        self.force_login_user(self._get_consultant().pk)
        response = self.client.post('/api/projects/5/asset-handovers/', data)

        self.assertForbidden(response)

    def test_forbid_create_by_subcontractor(self):
        data = self.load_request_fixture('/asset_handover/create_asset_handover_document.json')
        self.force_login_user(self._get_subcontractor().pk)
        response = self.client.post('/api/projects/5/asset-handovers/', data)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        response = self.client.post(
            '/api/projects/5/asset-handovers/',
            {'asset_handover': 5, 'document_type': 2, 'number_required_files': 3}
        )

        self.assertUnauthorized(response)

    def test_delete_by_superuser(self):
        self.force_login_user(self._get_superuser().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, 1)

    def test_delete_by_company_admin(self):
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, 1)

    def test_delete_by_admin(self):
        self.force_login_user(self._get_admin().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, 1)

    def test_delete_by_manager(self):
        self.force_login_user(self._get_manager().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, 1)

    def test_forbid_delete_by_subcontractor(self):
        self.force_login_user(self._get_subcontractor().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/1/')

        self.assertForbidden(response)

    def test_delete_by_client(self):
        self.force_login_user(self._get_client().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/1/')

        self.assertForbidden(response)

    def test_delete_by_consultant(self):
        self.force_login_user(self._get_consultant().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/1/')

        self.assertForbidden(response)

    def test_delete_by_package_activity_by_superuser(self):
        self.force_login_user(self._get_superuser().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/bulk-delete/', {'package_activity': 1})

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, {'package_activity_id': 1})
        # Make sure that asset handovers with other package activities weren't deleted.
        self.assertDatabaseHas(AssetHandover, {'package_activity_id': 2})
        self.assertDatabaseHas(AssetHandover, {'package_activity_id': 6})

    def test_delete_by_package_activity_by_company_admin(self):
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/bulk-delete/', {'package_activity': 1})

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, {'package_activity_id': 1})

    def test_delete_by_package_activity_by_admin(self):
        self.force_login_user(self._get_admin().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/bulk-delete/', {'package_activity': 1})

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, {'package_activity_id': 1})

    def test_delete_by_package_activity_by_manager(self):
        self.force_login_user(self._get_manager().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/bulk-delete/', {'package_activity': 1})

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandover, {'package_activity_id': 1})

    def test_forbid_delete_by_package_activity_by_client(self):
        self.force_login_user(self._get_client().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/bulk-delete/', {'package_activity': 1})

        self.assertForbidden(response)

    def test_forbid_delete_by_package_activity_by_consultant(self):
        self.force_login_user(self._get_client().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/bulk-delete/', {'package_activity': 1})

        self.assertForbidden(response)

    def test_forbid_delete_by_package_activity_by_subcontractor(self):
        self.force_login_user(self._get_client().pk)
        response = self.client.delete('/api/projects/5/asset-handovers/bulk-delete/', {'package_activity': 1})

        self.assertForbidden(response)

    def test_update_by_superuser(self):
        data = self.load_request_fixture('/asset_handover/update_asset_handover_document.json')
        self.force_login_user(self._get_superuser().pk)
        response = self.client.put('/api/projects/5/asset-handovers/8/', data)

        self.assertOk(response)

        for document in data['documents']:
            self.assertDatabaseHas(AssetHandoverDocument, {'asset_handover': 8, **document})

        self.assertDatabaseHas(AssetHandoverInformation, {'asset_handover': 8, **data['asset_handover_information']})

    def test_update_by_company_admin(self):
        data = self.load_request_fixture('/asset_handover/update_asset_handover_document.json')
        self.force_login_user(self._get_admin().pk)
        response = self.client.put('/api/projects/5/asset-handovers/8/', data)

        self.assertOk(response)

        for document in data['documents']:
            self.assertDatabaseHas(AssetHandoverDocument, {'asset_handover': 8, **document})

        self.assertDatabaseHas(AssetHandoverInformation, {'asset_handover': 8, **data['asset_handover_information']})

    def test_update_by_admin(self):
        data = self.load_request_fixture('/asset_handover/update_asset_handover_document.json')
        self.force_login_user(self._get_admin().pk)
        response = self.client.put('/api/projects/5/asset-handovers/8/', data)

        self.assertOk(response)

        for document in data['documents']:
            self.assertDatabaseHas(AssetHandoverDocument, {'asset_handover': 8, **document})

        self.assertDatabaseHas(AssetHandoverInformation, {
            'asset_handover': 8,
            **data['asset_handover_information']
        })

    def test_update_by_manager(self):
        data = self.load_request_fixture('/asset_handover/update_asset_handover_document.json')
        self.force_login_user(self._get_manager().pk)
        response = self.client.put('/api/projects/5/asset-handovers/8/', data)

        self.assertOk(response)

        for document in data['documents']:
            self.assertDatabaseHas(AssetHandoverDocument, {'asset_handover': 8, **document})

        self.assertDatabaseHas(AssetHandoverInformation, {
            'asset_handover': 8,
            **data['asset_handover_information']
        })

    def test_update_by_subcontractor(self):
        data = self.load_request_fixture('/asset_handover/update_asset_handover_document.json')
        self.force_login_user(self._get_subcontractor().pk)
        response = self.client.put('/api/projects/5/asset-handovers/8/', data)

        self.assertForbidden(response)

    def test_update_by_client(self):
        data = self.load_request_fixture('/asset_handover/update_asset_handover_document.json')
        self.force_login_user(self._get_client().pk)
        response = self.client.put('/api/projects/5/asset-handovers/8/', data)

        self.assertForbidden(response)

    def test_update_by_consultant(self):
        data = self.load_request_fixture('/asset_handover/update_asset_handover_document.json')
        self.force_login_user(self._get_consultant().pk)
        response = self.client.put('/api/projects/5/asset-handovers/8/', data)

        self.assertForbidden(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_superuser(self):
        superuser = self._get_superuser()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Asset Handover CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/asset_handover/csv_report_created.html'
            }
        ])

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        company_admin = self._get_company_admin()
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(company_admin.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertOk(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_admin.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertOk(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_manager.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertOk(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_consultant(self):
        project_consultant = self._get_consultant(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertOk(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_client(self):
        project_client = self._get_client(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertOk(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertOk(response)

    def test_forbid_get_csv_by_non_project_subcontractor(self):
        non_project_subcontractor = self._get_subcontractor(~Q(project=5))
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertForbidden(response)

    def test_forbid_get_csv_by_non_project_client(self):
        non_project_client = self._get_client(~Q(project=5))
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertForbidden(response)

    def test_forbid_get_csv_by_non_project_consultant(self):
        non_project_consultant = self._get_consultant(~Q(project=5))
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertForbidden(response)

    def test_forbid_get_csv_by_non_project_admin(self):
        non_project_admin = self._get_admin(~Q(project=5))
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_admin.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertForbidden(response)

    def test_forbid_get_csv_by_non_project_manager(self):
        non_project_manager = self._get_manager(~Q(project=5))
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self.force_login_user(non_project_manager.pk)
        response = self.client.get('/api/projects/5/asset-handovers/csv/')

        self.assertForbidden(response)

    def test_get_activities_with_filled_asset_handovers(self):
        self._log_in_as_superuser()
        response = self.client.get('/api/package-activities/', {'project': 5, 'expand': ['expanded_can_add_asset_handovers']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover/get_activities_with_filled_asset_handovers.json')
