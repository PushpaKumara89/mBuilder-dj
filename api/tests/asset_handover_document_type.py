from api.tests.test import TestCase, data_provider


class AssetHandoverDocumentTypeTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/asset_handover_document_types.json']

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': '-name'},
                '/asset_handover_document_types/get_all_desc_order.json',
            ),
        )

    @data_provider(get_filters)
    def test_search(self, filters, fixture):
        self.force_login_user(self._get_staff().pk)
        response = self.client.get('/api/asset-handover-document-types/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search(self):
        self.force_login_user(self._get_user(is_staff=False, is_superuser=False).pk)
        response = self.client.get('/api/asset-handover-document-types/', {'all': True})

        self.assertForbidden(response)
