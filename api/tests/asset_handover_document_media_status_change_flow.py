from freezegun import freeze_time

from api.models import AssetHandoverDocumentMedia, AssetHandoverDocumentMediaUpdate, AssetHandoverStatistics
from api.tests.test import TestCase


class AssetHandoverDocumentMediaStatusChangeFlowTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/asset_handover_document_media_status_flow.json']

    # Upload by subcontractor.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_upload_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        new_media = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                              'upload_asset_handover_document_media_update_by_subcontractor.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/', new_media)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': response.data['id'],
            'status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, {
            'asset_handover_document_media_id': response.data['id'],
            'new_data__status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
            'comment': None
        })

    # Re-upload by subcontractor

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_re_upload_by_project_subcontractor(self):
        superuser = self._get_superuser(project=5)
        self.force_login_user(superuser.pk)

        # Contest media.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Re-upload it.
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           're_upload_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    # Remove by subcontractor.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_in_progress_by_project_subcontractor(self):
        project_subcontractor = self._get_superuser(project=5)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_contested_by_project_subcontractor(self):
        # Contest media.
        superuser = self._get_superuser(project=5)
        self.force_login_user(superuser.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove it.
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_contested_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    # Upload by multiplex

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_upload_by_company_admin(self):
        creation_data = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                                  'upload_asset_handover_document_media_update.json')
        company_admin = self._get_company_admin()

        self.force_login_user(company_admin.pk)
        response = self.client.post('/api/projects/5/asset-handover-document-media/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {'asset_handover_document': 5, 'media': 2,
                                                            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL})
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, {
            'new_data__status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
            'asset_handover_document_media__asset_handover_document': 5,
            'asset_handover_document_media__media': 2,
            'comment': None,
            'user': company_admin.pk,
        })

        self.assertDatabaseHas(AssetHandoverStatistics, {
            'asset_handover_document': 5,
            'company': 1,
            'group': 1,
            'requesting_approval_count': 1,
            'project': 5
        })

    # Contest from in progress.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_contest_from_in_progress_by_company_admin(self):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_contest_from_in_progress_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_contest_from_in_progress_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_contest_from_in_progress_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from in_progress to contested."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_contest_from_in_progress_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from in_progress to contested."]}')

    # Undo contest from in progress.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_contest_from_in_progress_by_company_admin(self):
        # Contest.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_contest_to_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_contest_from_in_progress_by_project_admin(self):
        # Contest.
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_contest_to_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_contest_from_in_progress_by_project_manager(self):
        # Contest.
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'contest_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_contest_to_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    # Requesting approval from in progress.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_requesting_approval_from_in_progress_by_company_admin(self):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_requesting_approval_from_in_progress_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_requesting_approval_from_in_progress_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_requesting_approval_from_in_progress_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from in_progress to requesting_approval."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_requesting_approval_from_in_progress_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from in_progress to requesting_approval."]}')

    # Undo requesting approval to in progress.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_requesting_approval_to_in_progress_by_company_admin(self):
        # Request approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_requesting_approval_asset_handover_document_media_to_in_progress.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_requesting_approval_to_in_progress_by_project_manager(self):
        # Request approval
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_requesting_approval_asset_handover_document_media_to_in_progress.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_requesting_approval_to_in_progress_by_project_admin(self):
        # Request approval.
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_requesting_approval_asset_handover_document_media_to_in_progress.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.IN_PROGRESS,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_requesting_approval_to_in_progress_by_project_subcontractor(self):
        # Request approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_requesting_approval_asset_handover_document_media_to_in_progress.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to in_progress."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_requesting_approval_to_in_progress_by_project_client(self):
        # Request approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'requesting_approval_from_in_progress_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 2,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_requesting_approval_asset_handover_document_media_to_in_progress.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to in_progress."]}')

    # Accept rejected requesting approval.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_rejected_requesting_approval_by_company_admin(self):
        # Reject.
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 3,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Accept rejected approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 3,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_rejected_requesting_approval_by_project_manager(self):
        # Reject.
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 3,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Accept rejected approval.
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 3,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_rejected_requesting_approval_by_project_admin(self):
        # Reject.
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 3,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Accept rejected approval.
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 3,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_rejected_requesting_approval_by_project_subcontractor(self):
        # Reject.
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 3,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Accept rejected approval.
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requested_approval_rejected to contested."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_rejected_requesting_approval_by_project_client(self):
        # Reject.
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 3,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Accept rejected approval.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/3/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requested_approval_rejected to contested."]}')

    # Undo accept rejected requesting approval.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_accept_rejected_requesting_approval_by_company_admin(self):
        # Accept rejected approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_accept_rejected_requesting_approval_by_project_manager(self):
        # Accept rejected approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_accept_rejected_requesting_approval_by_project_admin(self):
        # Accept rejected approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_accept_rejected_requesting_approval_by_project_subcontractor(self):
        # Accept rejected approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from contested to requested_approval_rejected."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_accept_rejected_requesting_approval_by_project_client(self):
        # Accept rejected approval.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.CONTESTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_accept_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from contested to requested_approval_rejected."]}')

    # Decline rejected requesting approval.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_decline_rejected_requesting_approval_by_company_admin(self):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_decline_rejected_requesting_approval_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_decline_rejected_requesting_approval_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_decline_rejected_requesting_approval_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requested_approval_rejected to requesting_approval."]}')

    # Undo decline rejected requesting approval.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_decline_rejected_requesting_approval_by_company_admin(self):
        # Decline.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_decline_rejected_requesting_approval_by_project_manager(self):
        # Decline.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_decline_rejected_requesting_approval_by_project_admin(self):
        # Decline.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_decline_rejected_requesting_approval_by_project_subcontractor(self):
        # Decline.
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Undo action.
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_decline_rejected_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to requested_approval_rejected."]}')

    # Accept requesting approval.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_requesting_approval_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.ACCEPTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_requesting_approval_by_company_admin(self):
        company_admin = self._get_company_admin(is_superuser=False)
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to accepted."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_requesting_approval_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to accepted."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_requesting_approval_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to accepted."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_requesting_approval_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to accepted."]}')

    # Reject requesting approval.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_reject_requesting_approval_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_reject_requesting_approval_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to requested_approval_rejected."]}')

    # Undo reject requesting approval.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_reject_requesting_approval_by_project_client(self):
        # Action
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })

        # Undo action
        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_reject_requesting_approval_by_project_subcontractor(self):
        # Action
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })

        # Undo action
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'undo_reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requested_approval_rejected to requesting_approval."]}')

    # Remove from requesting approval.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requesting_approval_by_company_admin(self):
        company_admin = self._get_company_admin(is_superuser=False)
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requesting_approval_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requesting_approval_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requesting_approval_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to removed."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requesting_approval_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requesting_approval to removed."]}')

    # Remove from accepted approval rejected.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requested_approval_rejected_by_company_admin(self):
        # Move to requested_approval_rejected
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requested_approval_rejected_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requested_approval_rejected_by_project_admin(self):
        # Move to requested_approval_rejected
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requested_approval_rejected_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requested_approval_rejected_by_project_manager(self):
        # Move to requested_approval_rejected
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requested_approval_rejected_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requested_approval_rejected_by_project_subcontractor(self):
        # Move to requested_approval_rejected
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requested_approval_rejected_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requested_approval_rejected to removed."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_requested_approval_rejected_by_project_client(self):
        # Move to requested_approval_rejected
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'reject_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_requested_approval_rejected_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/2/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from requested_approval_rejected to removed."]}')

    # Remove from accepted.

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_accepted_by_company_admin(self):
        # Accept media
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.ACCEPTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_accepted_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_accepted_by_project_admin(self):
        # Accept media
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.ACCEPTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_accepted_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_accepted_by_project_manager(self):
        # Accept media
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.ACCEPTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_accepted_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.REMOVED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_accepted_by_project_subcontractor(self):
        # Accept media
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.ACCEPTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        project_subcontractor = self._get_subcontractor(project=5, company=1)
        self.force_login_user(project_subcontractor.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_accepted_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from accepted to removed."]}')

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_from_accepted_by_project_client(self):
        # Accept media
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'accept_requesting_approval_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertCreated(response)
        self.assertDatabaseHas(AssetHandoverDocumentMedia, {
            'pk': 4,
            'status': AssetHandoverDocumentMedia.Status.ACCEPTED,
        })
        self.assertDatabaseHas(AssetHandoverDocumentMediaUpdate, update)

        # Remove
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)

        update = self.load_request_fixture('/asset_handover_document_media_status_flow/'
                                           'remove_from_accepted_asset_handover_document_media.json')
        response = self.client.post('/api/projects/5/asset-handover-document-media/4/updates/', update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"status":["You cannot change status from accepted to removed."]}')
