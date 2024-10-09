from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import PackageHandoverDocumentMedia, PackageHandoverDocumentMediaUpdate, User
from api.tests.test import TestCase, data_provider


class PackageHandoverDocumentMediaUpdateTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/package_handovers.json',
        'api/tests/fixtures/dumps/package_handover_document.json'
    ]

    def test_set_uid_by_superuser(self):
        superuser = self._get_superuser()
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/set_uid_by_superuser.json')

        self.force_login_user(superuser.pk)
        response = self.client.post(
            '/api/projects/5/package-handover-document-media/1/updates/',
            new_package_handover_document_media_update
        )

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': superuser.pk, 'package_handover_document_media': 1,
             **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 1, **new_package_handover_document_media_update['new_data']}
        )

    def test_set_information_by_superuser(self):
        superuser = self._get_superuser()
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/set_information_by_superuser.json')

        self.force_login_user(superuser.pk)
        response = self.client.post(
            '/api/projects/5/package-handover-document-media/1/updates/',
            new_package_handover_document_media_update
        )

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': superuser.pk, 'package_handover_document_media': 1,
             **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 1, **new_package_handover_document_media_update['new_data']}
        )

    def test_accepted_by_superuser(self):
        superuser = self._get_superuser()
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/accepted_package_handover_document_media_by_client.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/1/updates/',
                                    new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': superuser.pk, 'package_handover_document_media': 1,
             **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 1, **new_package_handover_document_media_update['new_data']}
        )

    def test_contest_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/contest_package_handover_document_media_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/2/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_staff.pk, 'package_handover_document_media': 2, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 2, **new_package_handover_document_media_update['new_data']}
        )

    def test_remove_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/remove_package_handover_document_media_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/2/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_staff.pk, 'package_handover_document_media': 2, **new_package_handover_document_media_update}
        )
        self.assertSoftDeleted(
            PackageHandoverDocumentMedia,
            {'pk': 2, **new_package_handover_document_media_update['new_data']}
        )

    def test_undo_contest_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/undo_contest_package_handover_document_media_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/7/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'user': project_staff.pk,
                'package_handover_document_media': 7,
                'new_data': {'status': PackageHandoverDocumentMedia.Status.IN_PROGRESS.value},
                **new_package_handover_document_media_update
            }
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': 7,
                'status': PackageHandoverDocumentMedia.Status.IN_PROGRESS.value
            }
        )

    def test_move_from_requested_approval_rejected_to_contested_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/move_package_handover_document_media_from_requested_approval_rejected_to_contested_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/2/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_staff.pk, 'package_handover_document_media': 2, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 2, **new_package_handover_document_media_update['new_data']}
        )

    def test_undo_move_from_requested_approval_rejected_to_contested_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/undo_move_package_handover_document_media_from_requested_approval_rejected_to_contested_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/7/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_staff.pk, 'package_handover_document_media': 7, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 7, **new_package_handover_document_media_update['new_data']}
        )

    def test_move_from_requested_approval_rejected_to_requested_approval_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/move_package_handover_document_media_from_requested_approval_rejected_to_requested_approval_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/2/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_staff.pk, 'package_handover_document_media': 2, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 2, **new_package_handover_document_media_update['new_data']}
        )

    def test_undo_move_from_requested_approval_rejected_to_requested_approval_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/undo_move_package_handover_document_media_from_requested_approval_rejected_to_requested_approval_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/7/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_staff.pk, 'package_handover_document_media': 7, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 7, **new_package_handover_document_media_update['new_data']}
        )

    def test_request_approval_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/request_approval_package_handover_document_media_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/2/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_staff.pk, 'package_handover_document_media': 2, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 2, **new_package_handover_document_media_update['new_data']}
        )

    def test_undo_request_approval_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/undo_request_approval_package_handover_document_media_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/1/updates/',
                                    new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_staff.pk, 'package_handover_document_media': 1,
             **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 1, **new_package_handover_document_media_update['new_data']}
        )

    def test_accepted_by_client(self):
        project_client = self._get_client(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/accepted_package_handover_document_media_by_client.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/1/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_client.pk, 'package_handover_document_media': 1, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 1, **new_package_handover_document_media_update['new_data']}
        )

    def test_requested_approval_reject_by_client(self):
        project_client = self._get_client(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/requested_approval_reject_package_handover_document_media_by_client.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/1/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_client.pk, 'package_handover_document_media': 1, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 1, **new_package_handover_document_media_update['new_data']}
        )

    def test_undo_requested_approval_reject_by_client(self):
        project_client = self._get_client(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/undo_requested_approval_reject_package_handover_document_media_by_client.json')

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/8/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'user': project_client.pk, 'package_handover_document_media': 8,
             **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {'pk': 8, **new_package_handover_document_media_update['new_data']}
        )

    def test_reupload_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/reupload_package_handover_document_media_by_consultant.json')

        self.force_login_user(project_consultant.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/13/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'user': project_consultant.pk,
                'package_handover_document_media': 13,
                'new_data': { 'status': PackageHandoverDocumentMedia.Status.IN_PROGRESS.value },
                **new_package_handover_document_media_update
            }
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia,
            {
                'pk': 13,
                'status': PackageHandoverDocumentMedia.Status.IN_PROGRESS.value
            }
        )

    def test_remove_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/remove_package_handover_document_media_by_consultant.json')

        self.force_login_user(project_consultant.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/13/updates/', new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'user': project_consultant.pk,
                'package_handover_document_media': 13,
                'new_data': { 'status': PackageHandoverDocumentMedia.Status.REMOVED.value },
                **new_package_handover_document_media_update
            }
        )
        self.assertSoftDeleted(
            PackageHandoverDocumentMedia,
            {
                'pk': 13,
                'status': PackageHandoverDocumentMedia.Status.REMOVED.value
            }
        )

    def test_fail_reupload_by_staff_consultant(self):
        project_consultant = self._get_consultant(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/fail_reupload_package_handover_document_media_by_consultant.json')

        self.force_login_user(project_consultant.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/13/updates/', new_package_handover_document_media_update)

        self.assertBadRequest(response)

    def test_bulk_create_by_staff(self):
        project_staff = self._get_staff(project=5)
        package_handover_document = 2
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})
        self.force_login_user(project_staff.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertCreated(response)

        self.assertDatabaseHas(PackageHandoverDocumentMedia, {
            'package_handover_document': package_handover_document,
            'packagehandoverdocumentmediaupdate__old_data__status': PackageHandoverDocumentMedia.Status.IN_PROGRESS,
            'packagehandoverdocumentmediaupdate__new_data__status': PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
        })

    def test_bulk_create_invalid_transition_by_staff(self):
        project_staff = self._get_staff(project=5)
        package_handover_document = 2
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create_invalid_transition_by_staff.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})

        self.force_login_user(project_staff.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["This is not a valid status change."]}')

    def test_bulk_create_by_client(self):
        project_client = self._get_client(project=5)
        package_handover_document = 2
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create_by_client.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})
        self.force_login_user(project_client.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertCreated(response)

        self.assertDatabaseHas(PackageHandoverDocumentMedia, {
            'package_handover_document': package_handover_document,
            'packagehandoverdocumentmediaupdate__old_data__status': PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
            'packagehandoverdocumentmediaupdate__new_data__status': PackageHandoverDocumentMedia.Status.ACCEPTED,
        })

    def test_bulk_create_invalid_transition_by_client(self):
        project_client = self._get_client(project=5)
        package_handover_document = 1
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create_invalid_transition_by_client.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})
        self.force_login_user(project_client.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["This is not a valid status change."]}')

    def test_bulk_create_invalid_transition_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        package_handover_document = 2
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create_invalid_transition_by_consultant.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})
        self.force_login_user(project_consultant.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["This is not a valid status change."]}')

    def test_bulk_create_invalid_transition_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        package_handover_document = 1
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create_invalid_transition_by_subcontractor.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})
        self.force_login_user(project_subcontractor.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertBadRequest(response)
        self.assertEquals(response.content, b'{"non_field_errors":["This is not a valid status change."]}')

    def test_bulk_create_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        package_handover_document = 2
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create_by_consultant.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})
        self.force_login_user(project_consultant.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertCreated(response)

        self.assertSoftDeleted(PackageHandoverDocumentMedia, {
            'package_handover_document': package_handover_document,
            'packagehandoverdocumentmediaupdate__old_data__status': PackageHandoverDocumentMedia.Status.IN_PROGRESS,
            'packagehandoverdocumentmediaupdate__new_data__status': PackageHandoverDocumentMedia.Status.REMOVED,
        })

    def test_forbid_bulk_create_by_staff(self):
        project_staff = self._get_staff(~Q(project=5))
        package_handover_document = 2
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})

        self.force_login_user(project_staff.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertForbidden(response)

    def test_forbid_bulk_create_by_client(self):
        project_staff = self._get_client(project=5)
        package_handover_document = 2
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/forbid_bulk_create_by_client.json')
        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})

        self.force_login_user(project_staff.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertBadRequest(response)

    def test_forbid_bulk_create_by_consultant(self):
        project_staff = self._get_consultant(project=5)
        package_handover_document = 1
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_document_media_update/bulk_create.json')

        url = reverse('bulk_create_package_handover_document_media_updates', kwargs={'project_pk': 5, 'pk': package_handover_document})

        self.force_login_user(project_staff.pk)
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertForbidden(response)

    def test_forbid_remove_by_staff(self):
        project_staff = self._get_staff(project=5)
        new_package_handover_document_media_update = self.load_request_fixture('/package_handover_document_media_update/forbid_remove_package_handover_document_media_by_staff.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/5/package-handover-document-media/16/updates/', new_package_handover_document_media_update)

        self.assertBadRequest(response)

    def test_get_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-handover-document-media/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media_update/get_package_handover_document_media_update.json')

    def test_get_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media_update/get_package_handover_document_media_update.json')

    def test_forbid_get_by_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/6/package-handover-document-media/4/updates/4/')

        self.assertForbidden(response)

    def test_get_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media_update/get_package_handover_document_media_update.json')

    def test_forbid_get_by_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/3/updates/3/')

        self.assertForbidden(response)

    def test_get_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/13/updates/12/')

        self.assertOk(response)
        self.assertEqualsFixture(
            response.data,
            '/package_handover_document_media_update/get_consultant_package_handover_document_media_update.json'
        )

    def test_forbid_get_by_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/1/updates/1/')

        self.assertForbidden(response)

    def test_get_by_client(self):
        project_staff = self._get_client(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/5/package-handover-document-media/1/updates/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_document_media_update/get_package_handover_document_media_update_by_client.json')

    def test_forbid_get_by_client(self):
        project_staff = self._get_client(project=5)
        self.force_login_user(project_staff.pk)

        response = self.client.get('/api/projects/6/package-handover-document-media/4/updates/4/')

        self.assertForbidden(response)

    def get_filters_for_search(self):
        return (
            (
                {'all': True},
                '/package_handover_document_media_update/get_all_by_superuser.json',
                {'is_superuser': True},
                {'project_pk': 5, 'media_pk': 1}
            ),
            (
                {'page': 1, 'per_page': 3},
                '/package_handover_document_media_update/get_page_by_superuser.json',
                {'is_superuser': True},
                {'project_pk': 5, 'media_pk': 1}
            ),
            (
                {'page': 1, 'sort': '-created_at'},
                '/package_handover_document_media_update/get_page_by_superuser_with_sort_by_created_at.json',
                {'is_superuser': True},
                {'project_pk': 5, 'media_pk': 1}
            )
        )

    @data_provider(get_filters_for_search)
    def test_search(self, filters, fixture, user_params, package_handover_params):
        user = self._get_user(**user_params)
        self.force_login_user(user.pk)
        response = self.client.get('/api/projects/%s/package-handover-document-media/%s/updates/' % (package_handover_params['project_pk'], package_handover_params['media_pk']), filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)
