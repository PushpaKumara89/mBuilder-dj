from django.db.models import Q
from django.urls import reverse

from api.models import PackageHandoverDocument, PackageHandoverStatistics, PackageHandoverDocumentMedia, \
    PackageHandoverDocumentMediaUpdate, PackageMatrix, PackageHandover
from api.tests.test import TransactionTestCase


class PackageHandoverStatisticsTest(TransactionTestCase):
    WORKING_PROJECT = 5

    fixtures = [
        'api/tests/fixtures/dumps/package_handover_statistics.json',
    ]

    def test_create_package_handover_documents_by_superuser(self):
        new_package_handover_document = self.load_request_fixture('/package_handover_statistics/create_package_handover_document.json')
        url = reverse('package_handover_documents_list', kwargs={'project_pk': self.WORKING_PROJECT})

        self._log_in_as_superuser()
        response = self.client.post(url, new_package_handover_document)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocument, new_package_handover_document)
        self.assertDatabaseHas(PackageHandoverStatistics, {
            'package_handover_document': response.data['id'],
            'project_id': 5,
        })

    def test_create_package_handover_document_media_by_superuser(self):
        new_package_handover_document_media = self.load_request_fixture(
            '/package_handover_statistics/create_package_handover_document_media.json')
        url = reverse('package_handover_document_media_list', kwargs={'project_pk': self.WORKING_PROJECT})

        self._log_in_as_superuser()
        response = self.client.post(url, new_package_handover_document_media)

        self.assertCreated(response)
        self.assertDatabaseHas(PackageHandoverDocumentMedia, new_package_handover_document_media)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {
                'package_handover_document_media': response.data['id'],
                'new_data': {
                    'status': PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL.value,
                    'media': new_package_handover_document_media['media']
                }
            }
        )
        self.assertDatabaseHas(PackageHandoverStatistics, {
            'package_handover_document': new_package_handover_document_media['package_handover_document'],
            'in_progress_count': 1,
            'requesting_approval_count': 1
        })

        self.assertDatabaseHas(PackageHandoverStatistics, {
            'package_handover_document': new_package_handover_document_media['package_handover_document'],
            'requesting_approval_count': 1,
            'group': 1,
            'company': 1
        })

    def test_update_package_handover_document_media_by_superuser(self):
        updating_package_handover_document_media = 2
        new_package_handover_document_media_update = self.load_request_fixture(
            '/package_handover_statistics/update_package_handover_document_media.json'
        )
        url = reverse(
            'package_handover_document_media_updates_list',
            kwargs={'project_pk': self.WORKING_PROJECT, 'media_pk': updating_package_handover_document_media}
        )

        self._log_in_as_superuser()
        response = self.client.post(url, new_package_handover_document_media_update)

        self.assertCreated(response)
        self.assertDatabaseHas(
            PackageHandoverDocumentMediaUpdate,
            {'package_handover_document_media': updating_package_handover_document_media, **new_package_handover_document_media_update}
        )
        self.assertDatabaseHas(
            PackageHandoverDocumentMedia, {'pk': updating_package_handover_document_media, **new_package_handover_document_media_update['new_data']}
        )

        self.assertDatabaseHas(PackageHandoverStatistics, {
            'package_handover_document': 1,
            'in_progress_count': 2,
            'requesting_approval_count': 2
        })

        self.assertDatabaseHas(PackageHandoverStatistics, {
            'package_handover_document': 1,
            'in_progress_count': 0,
            'requesting_approval_count': 1,
            'company': 1,
            'group': 1
        })

    def test_delete_package_matrix(self):
        deleting_package_matrix = 5
        url = reverse('package_matrix_destroy', kwargs={'pk': deleting_package_matrix})
        self._log_in_as_superuser()
        response = self.client.delete(url)

        self.assertNoContent(response)
        self.assertSoftDeleted(PackageMatrix, deleting_package_matrix)

        package_handover_documents = list(
            PackageHandover.deleted_objects.filter(
                package_matrix=deleting_package_matrix
            ).values_list('packagehandoverdocument__id', flat=True)
        )
        for package_handover_document in package_handover_documents:
            self.assertSoftDeleted(PackageHandoverStatistics, {
                'package_handover_document': package_handover_document,
            })

    def test_get_package_handover_document_with_statistics(self):
        url = reverse('package_handover_documents_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 2
        })
        self._log_in_as_superuser()
        response = self.client.get(url, {'expand': ['expanded_package_handover_statistics']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_package_handover_document.json')

    def test_get_package_handover_document_with_statistics_filtered_by_company(self):
        url = reverse('package_handover_documents_list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_superuser()
        response = self.client.get(url, {'expand': ['expanded_package_handover_statistics'], 'company': [1]})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_package_handover_document_with_statistics_filtered_by_company.json')

    def test_get_package_handover_document_with_statistics_by_subcontractor(self):
        url = reverse('package_handover_documents_list_grouped', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'expand': ['expanded_package_handover_statistics']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_package_handover_document_with_statistics_by_subcontractor.json')

    def test_get_status_counter_by_superuser(self):
        self._log_in_as_superuser()
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_status_counter_by_superuser.json')

    def test_get_status_counter_by_company_admin(self):
        self._log_in_as_company_admin()
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_status_counter_by_company_admin.json')

    def test_get_status_counter_by_project_admin(self):
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_status_counter_by_project_admin.json')

    def test_get_status_counter_by_project_manager(self):
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_status_counter_by_project_manager.json')

    def test_get_status_counter_by_project_client(self):
        self._log_in_as_client(project=self.WORKING_PROJECT)
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_status_counter_by_project_client.json')

    def test_get_status_counter_by_non_project_admin(self):
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_status_counter_by_non_project_manager(self):
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_status_counter_by_non_project_client(self):
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_get_status_counter_by_project_subcontractor(self):
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_handover_statistics/get_status_counter_by_project_subcontractor.json')

    def test_get_status_counter_by_non_project_subcontractor(self):
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        url = reverse('package_handovers_statistics-project_status_counter', kwargs={'project_pk': self.WORKING_PROJECT})
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_package_handover_document_delete(self):
        deleting_package_handover_document = 1
        url = reverse('package_handover_documents_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_package_handover_document
        })
        self._log_in_as_superuser()
        response = self.client.delete(url)
        self.assertNoContent(response)

        self.assertSoftDeleted(PackageHandoverStatistics, {
            'package_handover_document': deleting_package_handover_document
        })

    def test_undelete_on_package_matrix_restore(self):
        working_project = 6
        package = 2
        package_activity = 2

        self._log_in_as_superuser()
        url = reverse('package_matrix_list', kwargs={'project_pk': working_project})
        response = self.client.post(url, {'package': package, 'package_activity': [package_activity]})

        self.assertCreated(response)
        # Check that entities restored.
        self.assertDatabaseHas(PackageMatrix, {
            'id': 7,
            'project': working_project,
            'package': package,
            'package_activity': package_activity
        })
        self.assertDatabaseHas(PackageHandover, {
            'package_matrix__project': working_project,
            'package_matrix__package': package,
            'package_matrix__package_activity': package_activity
        })
        self.assertDatabaseHas(PackageHandoverStatistics, {
            'package_handover_document__package_handover__package_matrix__project': working_project,
            'package_handover_document__package_handover__package_matrix__package': package,
            'package_handover_document__package_handover__package_matrix__package_activity': package_activity,
        })
