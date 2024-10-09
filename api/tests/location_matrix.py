from unittest import mock

import pendulum
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.db.models.expressions import Exists, OuterRef
from rest_framework.reverse import reverse

from api.models import LocationMatrix, LocationMatrixPackage, Task, TaskUpdate, User
from api.tests.test import TestCase, data_provider


class LocationMatrixTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/location_matrix.json']
    fss = FileSystemStorage()

    def mock_url_generate(self):
        return 'http://localhost/image.jpg'

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def test_create_by_project_staff_in_edit_mode(self):
        new_location_matrix = self.load_request_fixture('/location_matrix/new_location_matrix.json')
        project_staff_in_edit_mode = self._get_staff(project=6, editmode__project__pk=6)

        self.force_login_user(project_staff_in_edit_mode.pk)
        response = self.client.post('/api/projects/6/location-matrix/', new_location_matrix)

        self.assertCreated(response)
        self.assertDatabaseHas(LocationMatrix, {'project': 6, **new_location_matrix})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix__level': new_location_matrix['level'],
                                                       'location_matrix__building': new_location_matrix['building'],
                                                       'location_matrix__area': new_location_matrix['area'],
                                                       'location_matrix__project': 6,
                                                       'package_matrix__project': 6})
        self.assertEventsExist('/location_matrix/create_events_assertion.json')

    def test_create_by_superuser_in_edit_mode(self):
        new_location_matrix = self.load_request_fixture('/location_matrix/new_location_matrix.json')
        superuser = self._get_superuser(editmode__project=6)

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/6/location-matrix/', new_location_matrix)

        self.assertCreated(response)
        self.assertDatabaseHas(LocationMatrix, {'project': 6, **new_location_matrix})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix__level': new_location_matrix['level'],
                                                       'location_matrix__building': new_location_matrix['building'],
                                                       'location_matrix__area': new_location_matrix['area'],
                                                       'location_matrix__project': 6,
                                                       'package_matrix__project': 6})

    def test_forbid_create_for_not_in_edit_mode_project_staff(self):
        new_location_matrix = self.load_request_fixture('/location_matrix/new_location_matrix.json')
        project_staff_not_in_edit_mode = self._get_staff(~Q(editmode__project=5), project=5)

        self.force_login_user(project_staff_not_in_edit_mode.pk)
        response = self.client.post('/api/projects/5/location-matrix/', new_location_matrix)

        self.assertForbidden(response)

    def test_forbid_create_for_not_in_edit_mode_superuser(self):
        new_location_matrix = self.load_request_fixture('/location_matrix/new_location_matrix.json')
        superuser_not_in_edit_mode = self._get_superuser(~Q(editmode__project=5))

        self.force_login_user(superuser_not_in_edit_mode.pk)
        response = self.client.post('/api/projects/5/location-matrix/', new_location_matrix)

        self.assertForbidden(response)

    def test_get_location_buildings_by_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/locations/buildings/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_buildings.json')

    def test_get_location_buildings_by_subcontractor(self):
        project_subcontractor = self._get_user(project=1, groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/1/locations/buildings/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_buildings_by_subcontractor.json')

    def test_get_location_buildings_by_consultant(self):
        project_consultant = self._get_user(project=1, groups=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/1/locations/buildings/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_buildings_by_consultant.json')

    def test_get_location_buildings_by_client(self):
        project_client = self._get_user(project=1, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/1/locations/buildings/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_buildings_by_client.json')

    def test_forbid_get_location_buildings_by_subcontractor(self):
        non_project_subcontractor = self._get_user(~Q(project=3), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/3/locations/buildings/')

        self.assertForbidden(response)

    def test_forbid_get_location_buildings_by_consultant(self):
        non_project_consultant = self._get_user(~Q(project=3), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/3/locations/buildings/')

        self.assertForbidden(response)

    def test_forbid_get_location_buildings_by_client(self):
        non_project_client = self._get_user(~Q(project=3), groups=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/3/locations/buildings/')

        self.assertForbidden(response)

    def test_filter_location_buildings_by_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/locations/buildings/', {'level': '-2B'})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/filter_buildings.json')

    def test_get_location_levels_by_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/locations/levels/', {'all': 1, 'with_deleted': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_levels.json')

    def test_get_location_levels_by_subcontractor(self):
        project_subcontractor = self._get_user(project=1, groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/1/locations/levels/', {'all': 1, 'with_deleted': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_levels_by_subcontractor.json')

    def test_get_location_levels_by_consultant(self):
        project_consultant = self._get_user(project=1, groups=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/1/locations/levels/', {'all': 1, 'with_deleted': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_levels_by_consultant.json')

    def test_get_location_levels_by_client(self):
        project_client = self._get_user(project=1, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/1/locations/levels/', {'all': 1, 'with_deleted': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_levels_by_client.json')

    def test_get_location_levels_without_asset_handovers(self):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)
        response = self.client.get('/api/projects/1/locations/levels/',
                                   {'all': 1, 'exclude_where_asset_handover_exist': True, 'has_published_tasks': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_without_asset_handovers.json')

    def test_forbid_get_location_levels_by_subcontractor(self):
        non_project_subcontractor = self._get_user(~Q(project=3), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/3/locations/levels/', {'all': 1, 'with_deleted': True})

        self.assertForbidden(response)

    def test_forbid_get_location_levels_by_consultant(self):
        non_project_consultant = self._get_user(~Q(project=3), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/3/locations/levels/', {'all': 1, 'with_deleted': True})

        self.assertForbidden(response)

    def test_forbid_get_location_levels_by_client(self):
        non_project_client = self._get_user(~Q(project=3), groups=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/3/locations/levels/', {'all': 1, 'with_deleted': True})

        self.assertForbidden(response)

    def test_get_location_areas_by_project_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/locations/areas/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_areas.json')

    def test_get_location_areas_by_subcontractor(self):
        project_subcontractor = self._get_user(project=1, groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/1/locations/areas/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_areas_by_subcontractor.json')

    def test_get_location_areas_by_consultant(self):
        project_consultant = self._get_user(project=1, groups=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/1/locations/areas/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_areas_by_consultant.json')

    def test_get_location_areas_by_client(self):
        project_client = self._get_user(project=1, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/1/locations/areas/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_areas_by_client.json')

    def test_forbid_get_location_areas_by_subcontractor(self):
        non_project_subcontractor = self._get_user(~Q(project=3), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/3/locations/areas/')

        self.assertForbidden(response)

    def test_forbid_get_location_areas_by_consultant(self):
        non_project_consultant = self._get_user(~Q(project=3), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/3/locations/areas/')

        self.assertForbidden(response)

    def test_forbid_get_location_areas_by_client(self):
        non_project_client = self._get_user(~Q(project=3), groups=User.Group.CLIENT.value)
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/3/locations/areas/')

        self.assertForbidden(response)

    def test_forbid_get_location_areas_by_non_project_user(self):
        non_project_user = self._get_staff(~Q(project=1))
        self.force_login_user(non_project_user.pk)
        response = self.client.get('/api/projects/1/locations/areas/')

        self.assertForbidden(response)

    def get_area_filters(self):
        return (
            (
                {'building': 'Building A'},
                '/location_matrix/get_area_by_building.json'
            ),
            (
                {'level': '-2B'},
                '/location_matrix/get_area_by_level.json'
            ),
            (
                {'has_published_tasks': True},
                '/location_matrix/get_area_with_related_task.json'
            ),
            (
                {'building': 'Building A', 'level': '-2B'},
                '/location_matrix/get_area_by_building_and_level.json'
            ),
            (
                {'package': [4]},
                '/location_matrix/get_area_by_package.json'
            ),
            (
                {'package_activity': [3, 4]},
                '/location_matrix/get_areas_by_package_activity.json.json'
            ),
            (
                {'exclude': ['Group', 'Meeting room']},
                '/location_matrix/get_areas_without_related_to_floor_plans.json.json'
            ),
        )

    @data_provider(get_area_filters)
    def test_filter_area_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/locations/areas/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_update_by_project_staff(self):
        project_staff = self._get_staff(project__locationmatrix=5)
        update_location_matrix = self.load_request_fixture('/location_matrix/update_location_matrix.json')

        self.force_login_user(project_staff.pk)
        response = self.client.put('/api/location-matrix/5/', update_location_matrix)

        self.assertOk(response)
        self.assertDatabaseHas(LocationMatrix, {'pk': 5, **update_location_matrix})
        self.assertEventsExist('/location_matrix/update_events_assertion.json')

    def test_update_by_superuser(self):
        superuser = self._get_superuser(~Q(project__locationmatrix=5))
        update_location_matrix = self.load_request_fixture('/location_matrix/update_location_matrix.json')

        self.force_login_user(superuser.pk)
        response = self.client.put('/api/location-matrix/5/', update_location_matrix)

        self.assertOk(response)
        self.assertDatabaseHas(LocationMatrix, {'pk': 5, **update_location_matrix})

    def test_forbid_update_by_staff_from_another_project(self):
        update_location_matrix = self.load_request_fixture('/location_matrix/update_location_matrix.json')
        other_project_staff = self._get_staff(~Q(project__locationmatrix=5))

        self.force_login_user(other_project_staff.pk)
        response = self.client.put('/api/location-matrix/5/', update_location_matrix)

        self.assertForbidden(response)

    def test_forbid_update_by_non_staff(self):
        update_location_matrix = self.load_request_fixture('/location_matrix/update_location_matrix.json')
        non_staff = self._get_user(project__locationmatrix=5, is_staff=False, is_superuser=False)

        self.force_login_user(non_staff.pk)
        response = self.client.put('/api/location-matrix/5/', update_location_matrix)

        self.assertForbidden(response)

    def test_delete_by_project_staff_in_edit_mode(self):
        project_staff_in_edit_mode = self._get_staff(editmode__project__locationmatrix=5, project__locationmatrix=5)
        self.force_login_user(project_staff_in_edit_mode.pk)
        response = self.client.delete('/api/location-matrix/5/')

        self.assertNoContent(response)
        self.assertSoftDeleted(LocationMatrix, 5)
        self.assertSoftDeleted(LocationMatrixPackage, {'location_matrix': 5})
        self.assertEventsExist('/location_matrix/delete_events_assertion.json')

    def test_delete_by_superuser_in_edit_mode(self):
        superuser_in_edit_mode = self._get_superuser(~Q(project__locationmatrix=5), editmode__project__locationmatrix=5)
        self.force_login_user(superuser_in_edit_mode.pk)
        response = self.client.delete('/api/location-matrix/5/')

        self.assertNoContent(response)
        self.assertSoftDeleted(LocationMatrix, 5)
        self.assertSoftDeleted(LocationMatrixPackage, {'location_matrix': 5})

    def test_forbid_delete_for_project_staff_not_in_edit_mode(self):
        project_staff_not_in_edit_mode = self._get_staff(~Q(editmode__project__locationmatrix=5),
                                                         project__locationmatrix=5)
        self.force_login_user(project_staff_not_in_edit_mode.pk)
        response = self.client.delete('/api/location-matrix/5/')

        self.assertForbidden(response)

    def test_forbid_delete_for_superuser_not_in_edit_mode(self):
        superuser_not_in_edit_mode = self._get_superuser(~Q(editmode__project__locationmatrix=5),
                                                         ~Q(project__locationmatrix=5))
        self.force_login_user(superuser_not_in_edit_mode.pk)
        response = self.client.delete('/api/location-matrix/5/')

        self.assertForbidden(response)

    def test_get_by_project_staff(self):
        project_staff = self._get_staff(project__locationmatrix=5)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/location-matrix/5/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_location_matrix.json')

    def test_get_by_superuser(self):
        superuser = self._get_superuser(~Q(project__locationmatrix=5))
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/location-matrix/5/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/get_location_matrix.json')

    def test_forbid_get_by_project_non_staff(self):
        project_non_staff = self._get_user(project__locationmatrix=5, is_staff=False, is_superuser=False)
        self.force_login_user(project_non_staff.pk)
        response = self.client.get('/api/location-matrix/5/')

        self.assertForbidden(response)

    def test_forbid_get_by_staff_not_from_project(self):
        non_project_staff = self._get_staff(~Q(project__locationmatrix=5))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/location-matrix/5/')

        self.assertForbidden(response)

    def test_forbid_get_by_non_staff_not_from_project(self):
        non_staff = self._get_user(~Q(project__locationmatrix=5), is_staff=False, is_superuser=False)
        self.force_login_user(non_staff.pk)
        response = self.client.get('/api/location-matrix/5/')

        self.assertForbidden(response)

    def get_filters(self):
        return (
            (
                {'all': True},
                '/location_matrix/get_all.json'
            ),
            (
                {'all': True, 'sort': '-level'},
                '/location_matrix/get_all_desc_order.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/location_matrix/get_page_per_page.json'
            ),
            (
                {'all': True, 'has_published_tasks': True},
                '/location_matrix/get_all_only_has_published_tasks.json'
            ),
            (
                {'all': True, 'sort': 'level', 'building': ['Building A'], 'level': ['-2B', '-5A']},
                '/location_matrix/get_all_filtered_by_locations.json'
            ),
        )

    @data_provider(get_filters)
    def test_search_by_project_staff(self, filters, fixture):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/location-matrix/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_staff(self):
        non_project_staff = self._get_staff(~Q(project=1))
        self.force_login_user(non_project_staff.pk)
        response = self.client.get('/api/projects/1/location-matrix/', {'all': True})

        self.assertForbidden(response)

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser(~Q(project=1))
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/1/location-matrix/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_project_client(self, filters, fixture):
        project_client = self._get_user(project=1, groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/1/location-matrix/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_client(self):
        project_client = self._get_user(~Q(project=1), groups=User.Group.CLIENT.value)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/1/location-matrix/', {'all': True})

        self.assertForbidden(response)

    @data_provider(get_filters)
    def test_search_by_project_consultant(self, filters, fixture):
        project_consultant = self._get_user(project=1, groups=User.Group.CONSULTANT.value)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/1/location-matrix/', filters)
        self.assertOk(response)

        self.assertEqualsFixture(response.data, fixture)

    def test_search_by_non_project_consultant_from_same_company_as_project_user(self):
        non_project_consultant = self._get_user(Exists(User.objects.filter(project=1, company=OuterRef('company'))),
                                                ~Q(project=1), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/1/location-matrix/', {'all': True})

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_consultant(self):
        non_project_consultant = self._get_user(~Exists(User.objects.filter(project=1, company=OuterRef('company'))),
                                                ~Q(project=1), groups=User.Group.CONSULTANT.value)
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/1/location-matrix/', {'all': 1})

        self.assertForbidden(response)

    @data_provider(get_filters)
    def test_search_by_project_subcontractor(self, filters, fixture):
        project_subcontractor = self._get_user(project=1, groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/1/location-matrix/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_by_non_project_subcontractor_from_same_company_as_project_user(self):
        non_project_subcontractor = self._get_user(Exists(User.objects.filter(project=1, company=OuterRef('company'))),
                                                   ~Q(project=1), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/1/location-matrix/', {'all': True})

        self.assertForbidden(response)

    def test_search_by_non_project_subcontractor(self):
        non_project_subcontractor = self._get_user(~Exists(User.objects.filter(project=1, company=OuterRef('company'))),
                                                   ~Q(project=1), groups=User.Group.SUBCONTRACTOR.value)
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/1/location-matrix/', {'all': 1})

        self.assertForbidden(response)

    def test_sync_by_project_staff_in_edit_mode(self):
        project_staff_in_edit_mode = self._get_staff(project=1, editmode__project=1)
        sync_data = self.load_request_fixture('/location_matrix/sync_location_matrix.json')

        self.force_login_user(project_staff_in_edit_mode.pk)
        response = self.client.post('/api/projects/1/location-matrix/sync/', sync_data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/sync_all.json')
        self.assertDatabaseHas(LocationMatrix, {'project': 1, 'building': 'Building A', 'level': '7A', 'area': 'Hall'})
        self.assertDatabaseHas(LocationMatrix, {'project': 1, 'building': 'Building A', 'level': '-9A', 'area': 'Meeting room'})
        self.assertDatabaseHas(LocationMatrix, {'project': 2, 'building': 'Building A', 'level': '0A', 'area': 'Hall'})
        self.assertDatabaseHas(LocationMatrix, {'project': 1, 'building': 'Building F', 'level': '1A1', 'area': 'Hall 1'})
        self.assertDatabaseHas(LocationMatrix, {'project': 3, 'building': 'Building A', 'level': '1R', 'area': 'Kitchen'})
        self.assertDatabaseHas(LocationMatrix, {'project': 1, 'building': 'Building C', 'level': '2R', 'area': 'Bedroom'})
        self.assertDatabaseHas(LocationMatrix, {'project': 1, 'building': 'Building K', 'level': '-2U', 'area': 'Pool'})
        self.assertDatabaseHas(LocationMatrix, {'project': 1, 'building': 'Building C', 'level': '0X', 'area': 'Playroom'})
        self.assertDatabaseHas(LocationMatrix, {'project': 1, 'building': 'Building A', 'level': '-3A', 'area': 'Hall'})
        self.assertSoftDeleted(LocationMatrix, {'project': 1, 'building': 'Building A', 'level': '1R1', 'area': 'Soup'})
        self.assertSoftDeleted(LocationMatrix, {'project': 1, 'building': 'Building A', 'level': '1R2', 'area': 'Soup'})
        # Check that deleted location matrix and related entities restored
        self.assertDatabaseHas(LocationMatrix, {'project': 1, 'building': 'Building A', 'level': '0I3', 'area': 'Group'})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix': 22, 'package_matrix': 8, 'package': 4, 'package_activity': 3})
        self.assertDatabaseHas(Task, {'location_matrix': 22, 'package_activity': 3, 'package_activity_task': 4})
        self.assertDatabaseHas(TaskUpdate, {'pk': 4})
        self.assertDatabaseHas(TaskUpdate, {'pk': 5})
        self.assertHardDeleted(LocationMatrixPackage, {'location_matrix': 8, 'package_matrix': 8, 'enabled': True,
                                                       'package': 4, 'package_activity': 3})
        self.assertDatabaseMissing(Task, {'location_matrix': 8, 'package_activity': 3, 'package_activity_task': 3})
        self.assertHardDeleted(Task, {'location_matrix': 8, 'package_activity': 3, 'package_activity_task': 4})
        self.assertDatabaseHas(Task, {'location_matrix': 5, 'building': 'Building F', 'level': '1A1', 'area': 'Hall 1'})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix__area': 'Hall',
                                                       'location_matrix__building': 'Building A',
                                                       'location_matrix__level': '-3A',
                                                       'package_matrix': 7})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix__area': 'Hall',
                                                       'location_matrix__building': 'Building A',
                                                       'location_matrix__level': '-3A',
                                                       'package_matrix': 6})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix__area': 'Playroom',
                                                       'location_matrix__building': 'Building C',
                                                       'location_matrix__level': '0X',
                                                       'package_matrix': 7})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix__area': 'Playroom',
                                                       'location_matrix__building': 'Building C',
                                                       'location_matrix__level': '0X',
                                                       'package_matrix': 6})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix__area': 'Pool',
                                                       'location_matrix__building': 'Building K',
                                                       'location_matrix__level': '-2U',
                                                       'package_matrix': 7})
        self.assertDatabaseHas(LocationMatrixPackage, {'location_matrix__area': 'Pool',
                                                       'location_matrix__building': 'Building K',
                                                       'location_matrix__level': '-2U',
                                                       'package_matrix': 6})
        self.assertEventsExist('/location_matrix/sync_events_assertion.json')

    def test_sync_by_superuser_in_edit_mode(self):
        superuser_in_edit_mode = self._get_superuser(editmode__project=1)
        sync_data = self.load_request_fixture('/location_matrix/sync_location_matrix.json')

        self.force_login_user(superuser_in_edit_mode.pk)
        response = self.client.post('/api/projects/1/location-matrix/sync/', sync_data)

        self.assertOk(response)

    def test_sync_order(self):
        sync_data = self.load_request_fixture('/location_matrix/sync_location_matrix_order.json')
        project_staff = self._get_staff(project=1, editmode__project=1)

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/location-matrix/sync/', sync_data)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/location_matrix/sync_all_order.json')
        self.assertEventsExist('/location_matrix/sync_all_order_events_assertion.json')

    def test_forbid_sync_by_staff_from_another_project(self):
        another_project_staff = self._get_staff(~Q(project=1), editmode__project=1)
        sync_data = self.load_request_fixture('/location_matrix/sync_location_matrix.json')

        self.force_login_user(another_project_staff.pk)
        response = self.client.post('/api/projects/1/location-matrix/sync/', sync_data)

        self.assertForbidden(response)

    def test_forbid_sync_by_staff_not_in_edit_mode(self):
        project_staff = self._get_staff(~Q(editmode__project=1), project=1)
        sync_data = self.load_request_fixture('/location_matrix/sync_location_matrix.json')

        self.force_login_user(project_staff.pk)
        response = self.client.post('/api/projects/1/location-matrix/sync/', sync_data)

        self.assertForbidden(response)

    def test_forbid_sync_by_superuser_not_in_edit_mode(self):
        superuser = self._get_superuser(~Q(editmode__project=1))
        sync_data = self.load_request_fixture('/location_matrix/sync_location_matrix.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/1/location-matrix/sync/', sync_data)

        self.assertForbidden(response)

    def test_sync_with_castling(self):
        superuser = self._get_superuser(editmode__project=3)
        sync_data = self.load_request_fixture('/location_matrix/sync_location_matrix_with_castling.json')

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/3/location-matrix/sync/', sync_data)

        self.assertOk(response)
        self.assertDatabaseHas(LocationMatrix, {'id': 6, 'project': 3, 'building': "Building A", 'level': "1R", 'area': "Soup"})
        self.assertDatabaseHas(LocationMatrix, {'id': 7, 'project': 3, 'building': "Building A", 'level': "1R", 'area': "Kitchen"})
        self.assertEventsExist('/location_matrix/sync_with_castling_events_assertion.json')

    def test_get_qr_codes_by_project_staff(self):
        project_staff = self._get_staff(project=1)
        self.force_login_user(project_staff.pk)
        response = self.client.get('/api/projects/1/location-matrix/qr-codes/')

        self.assertOk(response)

    def test_forbid_get_qr_codes_by_project_non_staff(self):
        project_non_staff = self._get_user(project=1, is_staff=False, is_superuser=False)
        self.force_login_user(project_non_staff.pk)
        response = self.client.get('/api/projects/1/location-matrix/qr-codes/')

        self.assertForbidden(response)

    def test_forbid_get_qr_codes_by_staff_from_another_project(self):
        staff_from_another_project = self._get_staff(~Q(project=1))
        self.force_login_user(staff_from_another_project.pk)
        response = self.client.get('/api/projects/1/location-matrix/qr-codes/')

        self.assertForbidden(response)

    def test_get_qr_codes_by_superuser(self):
        superuser = self._get_superuser(~Q(project=3))
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/1/location-matrix/qr-codes/')

        self.assertOk(response)

    def handover_documents_filters(self):
        return (
            (
                {'has_handover_documents': 1, 'building': ['Building H']},
                '/location_matrix/get_with_handover_documents_filtered_by_building.json',
            ),
            (
                {'has_handover_documents': 1, 'level': ['-3']},
                '/location_matrix/get_with_handover_documents_filtered_by_level.json'
            ),
            (
                {'has_handover_documents': 1, 'area': ['Group']},
                '/location_matrix/get_with_handover_documents_filtered_by_area.json'
            ),
            (
                {'has_handover_documents': 1, 'package': [3]},
                '/location_matrix/get_with_handover_documents_filtered_by_package.json'
            ),
            (
                {'has_handover_documents': 1, 'package_activity': [1]},
                '/location_matrix/get_with_handover_documents_filtered_by_package_activity.json'
            ),
        )

    @data_provider(handover_documents_filters)
    def test_filter_by_handover_documents(self, filters: dict, fixture: str):
        self._log_in_as_superuser()
        url = reverse('locations_buildings', kwargs={'project_pk': 5})
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def handover_documents_filters_for_consultant(self):
        return (
            (
                {'has_handover_documents': 1, 'building': ['Building H']},
                '/location_matrix/get_by_consultant_with_handover_documents_filtered_by_building.json',
            ),
            (
                {'has_handover_documents': 1, 'level': ['-3']},
                '/location_matrix/get_by_consultant_with_handover_documents_filtered_by_level.json'
            ),
            (
                {'has_handover_documents': 1, 'area': ['Group']},
                '/location_matrix/get_by_consultant_with_handover_documents_filtered_by_area.json'
            ),
            (
                {'has_handover_documents': 1, 'package': [3]},
                '/location_matrix/get_by_consultant_with_handover_documents_filtered_by_package.json'
            ),
            (
                {'has_handover_documents': 1, 'package_activity': [1]},
                '/location_matrix/get_by_consultant_with_handover_documents_filtered_by_package_activity.json'
            ),
        )

    @data_provider(handover_documents_filters_for_consultant)
    def test_filter_by_handover_documents_by_consultant(self, filters: dict, fixture: str):
        self._log_in_as_consultant(project=5)
        url = reverse('locations_buildings', kwargs={'project_pk': 5})
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def handover_documents_filters_for_subcontractor(self):
        return (
            (
                {'has_handover_documents': 1, 'building': ['Building I']},
                '/location_matrix/get_by_subcontractor_with_handover_documents_filtered_by_building.json',
            ),
            (
                {'has_handover_documents': 1, 'level': ['-3']},
                '/location_matrix/get_by_subcontractor_with_handover_documents_filtered_by_level.json'
            ),
            (
                {'has_handover_documents': 1, 'area': ['Group']},
                '/location_matrix/get_by_subcontractor_with_handover_documents_filtered_by_area.json'
            ),
            (
                {'has_handover_documents': 1, 'package': [4]},
                '/location_matrix/get_by_subcontractor_with_handover_documents_filtered_by_package.json'
            ),
            (
                {'has_handover_documents': 1, 'package_activity': [1]},
                '/location_matrix/get_by_subcontractor_with_handover_documents_filtered_by_package_activity.json'
            ),
        )

    @data_provider(handover_documents_filters_for_subcontractor)
    def test_filter_by_handover_documents_by_subcontractor(self, filters: dict, fixture: str):
        self._log_in_as_subcontractor(project=5)
        url = reverse('locations_buildings', kwargs={'project_pk': 5})
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @mock.patch('api.storages.AzurePrivateReportStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateReportStorage.url', mock_url_generate)
    @mock.patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_get_csv_by_company_admin(self):
        pendulum.set_test_now(pendulum.datetime(2020, 1, 1, 00, 00))

        self._log_in_as_company_admin()
        response = self.client.get(reverse('location_matrix_generate_csv', kwargs={'project_pk': 5}))

        self.assertOk(response)

        self.assertEmailEquals([
            {
                'subject': 'Location Matrix CSV report has been generated',
                'from_email': 'MBuild Support <some_email@email.com>',
                'to': ['cool.brad@gmail.com'],
                'fixture': self.responses_fixtures_dir + '/location_matrix/csv_report_created.html'
            }
        ])
