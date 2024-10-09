from freezegun import freeze_time
from rest_framework.reverse import reverse

from api.models import AssetHandover, AssetHandoverStatistics, Project, PackageMatrix, AssetHandoverDocumentMedia, \
    AssetHandoverDocument
from api.tests.test import TransactionTestCase, data_provider


class AssetHandoverStatisticsTest(TransactionTestCase):
    fixtures = [
        'api/tests/fixtures/dumps/asset_handover_statistic.json',
    ]

    WORKING_PROJECT = 5

    def test_create_on_asset_handover_document_create(self):
        data = self.load_request_fixture('/asset_handover_statistic/create_asset_handover_document.json')
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

        self.assertDatabaseHas(AssetHandoverStatistics, {
            'asset_handover_document__asset_handover__location_matrix__building': data['building'],
            'asset_handover_document__asset_handover__location_matrix__level': data['level'],
            'asset_handover_document__asset_handover__location_matrix__area': data['area'],
            'asset_handover_document__asset_handover__package_activity': data['package_activity'],
            'asset_handover_document__document_type': 2,
            'asset_handover_document__number_required_files': 1
        })

        self.assertDatabaseHas(AssetHandoverStatistics, {
            'asset_handover_document__asset_handover__location_matrix__building': data['building'],
            'asset_handover_document__asset_handover__location_matrix__level': data['level'],
            'asset_handover_document__asset_handover__location_matrix__area': data['area'],
            'asset_handover_document__asset_handover__package_activity': data['package_activity'],
            'asset_handover_document__document_type': 2,
            'asset_handover_document__number_required_files': 1
        })

    def test_get_statistics_by_project_by_superuser(self):
        url = reverse('asset_handover_project_statistics', kwargs={'project_pk': 6})
        self._log_in_as_superuser()
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_project_statistics_by_superuser.json')

    def test_get_statistics_by_project_by_company_admin(self):
        url = reverse('asset_handover_project_statistics', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_company_admin()
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_project_statistics_by_company_admin.json')

    def test_get_statistics_by_project_by_admin(self):
        url = reverse('asset_handover_project_statistics', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_project_statistics_by_admin.json')

    def test_get_statistics_by_project_by_manager(self):
        url = reverse('asset_handover_project_statistics', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_project_statistics_by_manager.json')

    def test_get_statistics_by_project_by_client(self):
        url = reverse('asset_handover_project_statistics', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_project_statistics_by_client.json')

    def test_get_statistics_by_project_by_subcontractor(self):
        url = reverse('asset_handover_project_statistics', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_statistics_by_project_by_subcontractor.json')

    def test_get_statistics_by_project_by_consultant(self):
        url = reverse('asset_handover_project_statistics', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_statistics_by_project_by_consultant.json')

    def get_filters(self):
        return (
            (
                {'package': [2]},
                '/asset_handover_statistics/get_filtered_by_package.json'
            ),
            (
                {'package_activity': [6]},
                '/asset_handover_statistics/get_filtered_by_package_activity.json'
            ),
            (
                {'building': ['Building A']},
                '/asset_handover_statistics/get_filtered_by_building.json'
            ),
            (
                {'level': ['7A']},
                '/asset_handover_statistics/get_filtered_by_level.json'
            ),
            (
                {'area': ['Hall']},
                '/asset_handover_statistics/get_filtered_by_area.json'
            ),
        )

    @data_provider(get_filters)
    def test_get_filtered_statistics_by_superuser(self, filters, fixture):
        url = reverse('asset_handover_statistics-filtered', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_get_filtered_statistics_by_company_admin(self):
        url = reverse('asset_handover_statistics-filtered', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_company_admin()
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_filtered_statistics_by_company_admin.json')

    def test_get_filtered_statistics_by_admin(self):
        url = reverse('asset_handover_statistics-filtered', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_filtered_statistics_by_admin.json')

    def test_get_filtered_statistics_by_manager(self):
        url = reverse('asset_handover_statistics-filtered', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_filtered_statistics_by_manager.json')

    def test_get_filtered_statistics_by_client(self):
        url = reverse('asset_handover_statistics-filtered', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/get_filtered_statistics_by_client.json')

    def test_get_filtered_statistics_by_subcontractor(self):
        url = reverse('asset_handover_statistics-filtered', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_filtered_statistics_by_consultant(self):
        url = reverse('asset_handover_statistics-filtered', kwargs={'project_pk': self.WORKING_PROJECT})
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_on_asset_handover_document_update(self):
        data = self.load_request_fixture('/asset_handover_statistic/update_asset_handover_document.json')
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.put('/api/projects/5/asset-handovers/3/', data)

        self.assertOk(response)

        # Check that asset handover document statistics changed.
        self.assertDatabaseHas(AssetHandoverStatistics, {
            'asset_handover_document': 5,
            'project': self.WORKING_PROJECT,
            'required_files_count': 1,
            'requesting_approval_count': 1,
        })
        self.assertDatabaseHas(AssetHandoverStatistics, {
            'asset_handover_document': 6,
            'project': self.WORKING_PROJECT,
            'required_files_count': 6,
        })

    def test_on_project_delete(self):
        self._log_in_as_superuser()
        response = self.client.delete('/api/projects/5/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(Project, 5)
        self.assertDatabaseMissing(AssetHandoverStatistics, {
            'project_id': self.WORKING_PROJECT,
        })
        self.assertSoftDeleted(AssetHandoverStatistics, {
            'project_id': self.WORKING_PROJECT,
        })

    def test_on_package_activity_delete_from_project(self):
        self._log_in_as_staff(project__packagematrix=2)
        response = self.client.delete('/api/package-matrix/2/')

        self.assertNoContent(response)
        self.assertSoftDeleted(PackageMatrix, 2)

        self.assertSoftDeleted(AssetHandover, {
            'location_matrix__locationmatrixpackage__package_matrix': 2
        })

        self.assertSoftDeleted(AssetHandoverStatistics, {
            'project': self.WORKING_PROJECT,
            'asset_handover_document__asset_handover__location_matrix__locationmatrixpackage__package_matrix': 2,
            'asset_handover_document__document_type': 1
        })
        self.assertSoftDeleted(AssetHandoverStatistics, {
            'project': self.WORKING_PROJECT,
            'asset_handover_document__asset_handover__location_matrix__locationmatrixpackage__package_matrix': 2,
            'asset_handover_document__document_type': 2
        })

    def test_on_asset_handover_document_media_create(self):
        working_asset_hanover_document_id = 5
        creation_data = self.load_request_fixture('/asset_handover_statistic/create_asset_handover_document_media.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia,
                               {'asset_handover_document': working_asset_hanover_document_id, 'media': 2, 'uid': creation_data['uid']})

        self.assertDatabaseHas(AssetHandoverStatistics, {
            'asset_handover_document': working_asset_hanover_document_id,
            'project_id': self.WORKING_PROJECT,
            'requesting_approval_count': 2,
            'group': None,
            'company': None
        })

        self.assertDatabaseHas(AssetHandoverStatistics, {
            'asset_handover_document': working_asset_hanover_document_id,
            'project_id': self.WORKING_PROJECT,
            'requesting_approval_count': 1,
            'group': 1,
            'company': 1
        })

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_on_asset_handover_document_media_update(self):
        working_asset_handover_document_media_id = 3
        update = self.load_request_fixture('/asset_handover_statistic/contest_from_in_progress_asset_handover_document_media.json')
        url = reverse('asset_handover_document_media_update_list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'media_pk': working_asset_handover_document_media_id
        })

        self._log_in_as_superuser()
        response = self.client.post(url, update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': working_asset_handover_document_media_id,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })

        self.assertDatabaseHas(AssetHandoverStatistics, {
            'project': self.WORKING_PROJECT,
            'contested_count': 1,
            'group': None,
            'company': None,
            'asset_handover_document__assethandoverdocumentmedia': working_asset_handover_document_media_id
        })

        self.assertDatabaseHas(AssetHandoverStatistics, {
            'project': self.WORKING_PROJECT,
            'contested_count': 2,
            'in_progress_count': 0,
            'group': 1,
            'company': 1,
            'asset_handover_document__assethandoverdocumentmedia': working_asset_handover_document_media_id
        })

    def test_get_asset_handover_with_statistics(self):
        self._log_in_as_superuser()
        url = reverse('asset_handover_list', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url, {'expand': ['expanded_asset_handover_documents.expanded_asset_handover_statistics']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/search_asset_handover_with_expanded_statistics.json')

    def test_get_asset_handover_with_statistics_filtered_by_company(self):
        self._log_in_as_superuser()
        url = reverse('asset_handover_list', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url, {'expand': ['expanded_asset_handover_documents.expanded_asset_handover_statistics'], 'company': [1]})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/search_asset_handover_with_expanded_statistics_filtered_by_company.json')

    def test_get_asset_handover_with_statistics_by_subcontractor(self):
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        url = reverse('asset_handover_list', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url, {'expand': ['expanded_asset_handover_documents.expanded_asset_handover_statistics']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_statistics/search_by_subcontractor_asset_handover_with_expanded_statistics.json')
