from api.models import User, AssetHandoverDocument
from api.tests.test import TestCase, data_provider


class AssetHandoverDocumentTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/asset_handover_document_media_update.json']

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': 'id', 'expand': [
                    'expanded_asset_handover_document_media.expanded_upload_update.expanded_user',
                    'expanded_asset_handover_document_media.expanded_upload_update.expanded_user.expanded_user_company',
                ]},
                '/asset_handover_documents/get_by_company_admin_all_desc_order.json',
                {'groups': User.Group.COMPANY_ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_documents/get_by_admin_all_desc_order.json',
                {'groups': User.Group.ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_documents/get_by_manager_all_desc_order.json',
                {'groups': User.Group.MANAGER.value}
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_documents/get_by_subcontractor_all_desc_order.json',
                {'groups': User.Group.SUBCONTRACTOR.value, 'project': 5, 'company': 1}
            ),
            (
                {'all': True, 'sort': 'id'},
                '/asset_handover_documents/get_by_client_all_desc_order.json',
                {'groups': User.Group.CLIENT.value, 'project': 5}
            ),
            (
                {'all': True, 'sort': 'id', 'building': 'Building A'},
                '/asset_handover_documents/filtered_by_building.json',
                {'groups': User.Group.ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id', 'level': '7A'},
                '/asset_handover_documents/filtered_by_level.json',
                {'groups': User.Group.ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id', 'area': 'Hall'},
                '/asset_handover_documents/filtered_by_area.json',
                {'groups': User.Group.ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id', 'package': [2]},
                '/asset_handover_documents/filtered_by_package.json',
                {'groups': User.Group.ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id', 'package_activity': [2]},
                '/asset_handover_documents/filtered_by_package_activity.json',
                {'groups': User.Group.ADMIN.value}
            ),
            (
                {'all': True, 'sort': 'id', 'user': [2]},
                '/asset_handover_documents/filtered_by_user.json',
                {'groups': User.Group.ADMIN.value}
            ),
            (
                {'company': [2]},
                '/asset_handover_documents/filtered_by_company.json',
                {'groups': User.Group.ADMIN.value}
            ),
        )

    @data_provider(get_filters)
    def test_search(self, filters, fixture, user_filters):
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.get('/api/projects/5/asset-handover-documents/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/asset-handover-documents/', {'all': True})

        self.assertUnauthorized(response)

    def test_delete_by_company_admin(self):
        self.force_login_user(self._get_company_admin().pk)
        response = self.client.delete('/api/projects/5/asset-handover-documents/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandoverDocument, 1)

    def test_delete_by_admin(self):
        self.force_login_user(self._get_admin().pk)
        response = self.client.delete('/api/projects/5/asset-handover-documents/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandoverDocument, 1)

    def test_delete_by_manager(self):
        self.force_login_user(self._get_manager().pk)
        response = self.client.delete('/api/projects/5/asset-handover-documents/1/')

        self.assertNoContent(response)
        self.assertDatabaseMissing(AssetHandoverDocument, 1)

    def forbid_delete_users_filters(self):
        return (
            ({'groups': User.Group.CLIENT.value, 'project': 5},),
            ({'groups': User.Group.CONSULTANT.value, 'project': 5},),
            ({'groups': User.Group.SUBCONTRACTOR.value, 'project': 5},),
        )

    @data_provider(forbid_delete_users_filters)
    def test_forbid_delete(self, user_filters):
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.delete('/api/projects/5/asset-handover-documents/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/asset-handover-documents/1/')

        self.assertUnauthorized(response)

    def forbid_update_users_filters(self):
        return (
            ({'groups': User.Group.CLIENT.value, 'project': 5},),
            ({'groups': User.Group.CONSULTANT.value, 'project': 5},),
            ({'groups': User.Group.SUBCONTRACTOR.value, 'project': 5},),
        )

    @data_provider(forbid_update_users_filters)
    def test_forbid_update(self, user_filters):
        update_fixture = self.load_request_fixture('/asset_handover_document/update_asset_handover_document.json')
        self.force_login_user(self._get_user(**user_filters).pk)
        response = self.client.put('/api/projects/5/asset-handover-documents/1/', update_fixture)

        self.assertForbidden(response)

    def get_filters_for_search_package_activities_with_asset_handovers(self):
        return (
            (
                {'has_asset_handovers': True, 'project': 8, 'package': 2, 'with_deleted_asset_handovers': True},
                '/asset_handover_documents/get_package_activities_with_asset_handovers_by_superuser.json',
                {'user_pk': self._get_superuser().pk}
            ),
            (
                {'has_asset_handovers': True, 'project': 8, 'package': 2},
                '/asset_handover_documents/get_package_activities_with_asset_handovers_by_consultant.json',
                {'user_pk': self._get_consultant(project=8).pk}
            ),
            (
                {'has_asset_handovers': True, 'project': 8, 'package': 2},
                '/asset_handover_documents/get_package_activities_with_asset_handovers_by_first_subcontractor.json',
                {'user_pk': self._get_subcontractor(project=8, company=4).pk}
            ),
            (
                {'has_asset_handovers': True, 'project': 8, 'package': 2},
                '/asset_handover_documents/get_package_activities_with_asset_handovers_by_second_subcontractor.json',
                {'user_pk': self._get_subcontractor(project=8, company=1).pk}
            ),
        )

    @data_provider(get_filters_for_search_package_activities_with_asset_handovers)
    def test_search_package_activities_with_asset_handovers(self, filters, fixture, params):
        self.force_login_user(params['user_pk'])
        response = self.client.get('/api/package-activities/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_by_consultant(self):
        self.force_login_user(self._get_consultant(project=5).pk)
        response = self.client.get('/api/projects/5/asset-handover-documents/', {'all': True, 'sort': 'id'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_documents/search_by_consultant.json')

    def test_search_by_client(self):
        self.force_login_user(self._get_client(project=5).pk)
        response = self.client.get('/api/projects/5/asset-handover-documents/', {'all': True, 'sort': 'id', 'expand': ['expanded_asset_handover_document_media']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/asset_handover_documents/search_by_client.json')
