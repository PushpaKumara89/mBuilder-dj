from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.db.models.expressions import Exists, OuterRef
from django.urls import reverse

from api.models import PackageMatrix, LocationMatrixPackage, Task, Subtask, User, ProjectUser
from api.tests.test import TestCase


class PackageMatrixTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/package_matrix.json']
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    WORKING_PROJECT = 5

    def test_list_matrix_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/package-matrix/',
                                   {'expand': ['expanded_companies', 'expanded_package', 'expanded_package_activity']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_matrix/list_package_matrix.json')

    def test_list_matrix_by_project_staff(self):
        project_staff = self._get_staff(project=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/5/package-matrix/',
                                   {'expand': ['expanded_companies', 'expanded_package', 'expanded_package_activity']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/package_matrix/list_package_matrix.json')

    def test_forbid_get_matrix_by_staff_from_other_project(self):
        staff = self._get_staff(~Q(project=5))
        self.force_login_user(staff.pk)
        response = self.client.get('/api/projects/5/package-matrix/')

        self.assertForbidden(response)

    def test_forbid_list_matrix_by_subcontractor_without_project_users_with_same_company(self):
        subcontractor = self._get_user(~Exists(ProjectUser.objects.filter(project=7, user__company=OuterRef('company'))),
                                       groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(subcontractor.pk)
        response = self.client.get('/api/projects/7/package-matrix/')

        self.assertForbidden(response)

    def test_unauthorized_get_matrix(self):
        response = self.client.get('/api/projects/5/package-matrix/')

        self.assertUnauthorized(response)

    def test_create_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/6/package-matrix/', {'package': 2, 'package_activity': [2, 3]})

        self.assertCreated(response)
        # Check that deleted matrix restored
        self.assertDatabaseHas(PackageMatrix, {'project': 6, 'package': 2, 'package_activity': 2})

        self.assertDatabaseHas(PackageMatrix, {'project': 6, 'package': 2, 'package_activity': 3})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix': 3, 'package': 2, 'enabled': False,
                                                       'package_activity': 2})
        self.assertEqual(LocationMatrixPackage.objects.filter(location_matrix__project=6, package_matrix__package=2,
                                                              package_matrix__package_activity=2).count(), 4)
        self.assertEqual(LocationMatrixPackage.objects.filter(location_matrix__project=6, package_matrix__package=2,
                                                              package_matrix__package_activity=3).count(), 4)

    def test_create_by_project_staff(self):
        project_staff = self._get_staff(project=6)
        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/6/package-matrix/', {'package': 2, 'package_activity': [2, 3]})

        self.assertCreated(response)

    def test_forbid_create_not_in_edit_mode(self):
        staff = self._get_staff(~Q(editmode__project=5))
        self.force_login_user(staff.pk)
        response = self.client.post('/api/projects/5/package-matrix/', {'package': 3, 'package_activity': [1, 2]})

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        response = self.client.post('/api/projects/5/package-matrix/', {'package': 3, 'package_activity': [1, 2]})

        self.assertUnauthorized(response)

    def test_create_existing_matrix_relation_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/package-matrix/', {'package': 4, 'package_activity': 2})

        self.assertBadRequest(response)

    def test_delete_by_project_staff(self):
        project_staff = self._get_staff(project__packagematrix=1)
        self.force_login_user(project_staff.pk)
        response = self.client.delete('/api/package-matrix/1/')

        self.assertNoContent(response)

        self.assertSoftDeleted(PackageMatrix, 1)
        self.assertSoftDeleted(LocationMatrixPackage, 4)
        self.assertHardDeleted(Task, 1)
        self.assertHardDeleted(Subtask, 1)
        self.assertEventsExist('/package_matrix/destroy_events_assertion.json')

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/package-matrix/1/')

        self.assertNoContent(response)

    def test_forbid_delete_by_staff_from_other_project(self):
        staff = self._get_staff(~Q(project__packagematrix=1))
        self.force_login_user(staff.pk)
        response = self.client.delete('/api/package-matrix/1/')

        self.assertForbidden(response)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_company_admin()
        response = self.client.get(reverse('package_matrix_generate_csv', kwargs={'project_pk': self.WORKING_PROJECT}))

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Package Matrix CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/package_matrix/csv_report_created.html'
            }
        ])
