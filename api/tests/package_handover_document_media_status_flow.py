from freezegun import freeze_time

from api.models import PackageHandoverDocumentMedia
from api.tests.test import TestCase


class PackageHandoverDocumentMediaStatusFlowTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/package_handovers.json',
        'api/tests/fixtures/dumps/package_handover_document_media_status_flow.json'
    ]

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_upload_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        new_media = self.load_request_fixture('/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': response.data['id'],
                'last_confirmed_update': response.data['last_confirmed_update']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_upload_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        new_media = self.load_request_fixture(
            '/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        remove_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/remove_package_handover_document_media_by_subcontractor.json')
        remove_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            remove_update)

        self.assertCreated(remove_update_response)
        self.assertSoftDeleted(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': remove_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_contest_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture('/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        contest_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/contest_package_handover_document_media.json')
        contest_update_response = self.client.post('/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'], contest_update)

        self.assertCreated(contest_update_response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': contest_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_remove_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture(
            '/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        contest_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/contest_package_handover_document_media.json')
        contest_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            contest_update)
        self.assertCreated(contest_update_response)

        remove_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/remove_package_handover_document_media.json')
        remove_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            remove_update)

        self.assertCreated(remove_update_response)
        self.assertSoftDeleted(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': remove_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_contest_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture(
            '/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        contest_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/contest_package_handover_document_media.json')
        contest_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            contest_update)
        self.assertCreated(contest_update_response)

        undo_contest_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/undo_contest_package_handover_document_media.json')
        undo_contest_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            undo_contest_update)
        self.assertCreated(undo_contest_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': new_media_response.data['last_confirmed_update']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_reupload_by_subcontractor(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture('/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        contest_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/contest_package_handover_document_media.json')
        contest_update_response = self.client.post('/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'], contest_update)
        self.assertCreated(contest_update_response)

        self.force_login_user(subcontractor.pk)
        reupload_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/reupload_package_handover_document_media.json')
        reupload_update_response = self.client.post('/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'], reupload_update)

        self.assertCreated(reupload_update_response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': reupload_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_request_approval_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture('/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post('/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'], request_approval_update)

        self.assertCreated(request_approval_update_response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': request_approval_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_request_approval_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture(
            '/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            request_approval_update)
        self.assertCreated(request_approval_update_response)

        undo_request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/undo_request_approval_package_handover_document_media.json')
        undo_request_approval_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            undo_request_approval_update)
        self.assertCreated(undo_request_approval_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': new_media_response.data['last_confirmed_update']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_request_approval_by_client(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture('/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post('/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'], request_approval_update)
        self.assertCreated(request_approval_update_response)

        client = self._get_client(project=5)
        self.force_login_user(client.pk)
        accept_update = self.load_request_fixture('/package_handover_document_media_status_flow/accept_package_handover_document_media.json')
        accept_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            accept_update)
        self.assertCreated(accept_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': accept_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_reject_request_approval_by_client(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture('/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post('/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'], request_approval_update)
        self.assertCreated(request_approval_update_response)

        client = self._get_client(project=5)
        self.force_login_user(client.pk)
        reject_update = self.load_request_fixture('/package_handover_document_media_status_flow/reject_approval_request_package_handover_document_media.json')
        reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            reject_update)
        self.assertCreated(reject_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': reject_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_reject_request_approval_by_client(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture('/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post('/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'], request_approval_update)
        self.assertCreated(request_approval_update_response)

        client = self._get_client(project=5)
        self.force_login_user(client.pk)
        reject_update = self.load_request_fixture('/package_handover_document_media_status_flow/reject_approval_request_package_handover_document_media.json')
        reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            reject_update)
        self.assertCreated(reject_update_response)

        undo_reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/undo_reject_approval_request_package_handover_document_media.json')
        undo_reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            undo_reject_update)
        self.assertCreated(undo_reject_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': request_approval_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_decline_reject_request_approval_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture(
            '/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            request_approval_update)
        self.assertCreated(request_approval_update_response)

        client = self._get_client(project=5)
        self.force_login_user(client.pk)
        reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/reject_approval_request_package_handover_document_media.json')
        reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            reject_update)
        self.assertCreated(reject_update_response)

        self.force_login_user(staff.pk)
        decline_reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/decline_reject_approval_request_package_handover_document_media.json')
        decline_reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            decline_reject_update)
        self.assertCreated(decline_reject_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': decline_reject_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_decline_reject_request_approval_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture(
            '/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            request_approval_update)
        self.assertCreated(request_approval_update_response)

        client = self._get_client(project=5)
        self.force_login_user(client.pk)
        reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/reject_approval_request_package_handover_document_media.json')
        reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            reject_update)
        self.assertCreated(reject_update_response)

        self.force_login_user(staff.pk)
        decline_reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/decline_reject_approval_request_package_handover_document_media.json')
        decline_reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            decline_reject_update)
        self.assertCreated(decline_reject_update_response)

        undo_decline_reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/undo_decline_reject_approval_request_package_handover_document_media.json')
        undo_decline_reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            undo_decline_reject_update)
        self.assertCreated(undo_decline_reject_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': reject_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_accept_reject_request_approval_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture(
            '/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            request_approval_update)
        self.assertCreated(request_approval_update_response)

        client = self._get_client(project=5)
        self.force_login_user(client.pk)
        reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/reject_approval_request_package_handover_document_media.json')
        reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            reject_update)
        self.assertCreated(reject_update_response)

        self.force_login_user(staff.pk)
        accept_reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/accept_reject_approval_request_package_handover_document_media.json')
        accept_reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            accept_reject_update)
        self.assertCreated(accept_reject_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': accept_reject_update_response.data['id']
            }
        )

    @freeze_time("Jan 14th, 2020", auto_tick_seconds=15)
    def test_undo_accept_reject_request_approval_by_staff(self):
        subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(subcontractor.pk)

        new_media = self.load_request_fixture(
            '/package_handover_document_media_status_flow/create_package_handover_document_media.json')
        new_media_response = self.client.post('/api/projects/5/package-handover-document-media/', new_media)
        self.assertCreated(new_media_response)

        staff = self._get_staff(project=5)
        self.force_login_user(staff.pk)
        request_approval_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/request_approval_package_handover_document_media.json')
        request_approval_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            request_approval_update)
        self.assertCreated(request_approval_update_response)

        client = self._get_client(project=5)
        self.force_login_user(client.pk)
        reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/reject_approval_request_package_handover_document_media.json')
        reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            reject_update)
        self.assertCreated(reject_update_response)

        self.force_login_user(staff.pk)
        accept_reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/accept_reject_approval_request_package_handover_document_media.json')
        accept_reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            accept_reject_update)
        self.assertCreated(accept_reject_update_response)

        undo_accept_reject_update = self.load_request_fixture(
            '/package_handover_document_media_status_flow/undo_accept_reject_approval_request_package_handover_document_media.json')
        undo_accept_reject_update_response = self.client.post(
            '/api/projects/5/package-handover-document-media/%s/updates/' % new_media_response.data['id'],
            undo_accept_reject_update)
        self.assertCreated(undo_accept_reject_update_response)

        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': new_media_response.data['id'],
                'last_confirmed_update': reject_update_response.data['id']
            }
        )
