from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.urls import reverse

from api.models import FloorPlan, FloorPlanImage, FloorPlanAreaPin, FloorPlanArea
from api.tests.test import TestCase, data_provider


class FloorPlanTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/floor_plans.json',
    ]
    fss = FileSystemStorage()

    WORKING_PROJECT = 5

    # Test creation.

    def test_create_by_superuser(self):
        fixture_path = f'{self.requests_fixtures_dir}/floor_plans/test.pdf'
        self.load_and_save_fake_pdf(path=fixture_path, name='broom.pdf')

        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan_from_pdf.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(FloorPlan, {'project': 5, **creation_data})
        self.assertDatabaseHas(FloorPlanImage, {'plan': creation_data['media']})

    def test_create_by_company_admin(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        company_admin = self._get_company_admin()

        self.force_login_user(company_admin.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(FloorPlan, {'project': 5, **creation_data})

    def test_create_by_project_admin(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        project_admin = self._get_admin(project=5)

        self.force_login_user(project_admin.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(FloorPlan, {'project': 5, **creation_data})

    def create_by_project_manager(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        project_manager = self._get_manager(project=5)

        self.force_login_user(project_manager.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertCreated(response)
        self.assertDatabaseHas(FloorPlan, {'project': 5, **creation_data})

    def test_create_with_package_from_another_project(self):
        creation_data = self.load_request_fixture('/floor_plans/create_with_invalid_package.json')
        superuser = self._get_superuser()

        self.force_login_user(superuser.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertBadRequest(response)

    def test_forbid_create_by_non_project_admin(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        non_project_admin = self._get_admin(~Q(project=5))

        self.force_login_user(non_project_admin.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_manager(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        non_project_manager = self._get_manager(~Q(project=5))

        self.force_login_user(non_project_manager.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_project_consultant(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        project_consultant = self._get_consultant(project=5)

        self.force_login_user(project_consultant.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_project_subcontractor(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        project_subcontractor = self._get_subcontractor(project=5)

        self.force_login_user(project_subcontractor.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_project_client(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        project_client = self._get_client(project=5)

        self.force_login_user(project_client.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_consultant(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        non_project_consultant = self._get_consultant(~Q(project=5))

        self.force_login_user(non_project_consultant.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_subcontractor(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        non_project_subcontractor = self._get_subcontractor(~Q(project=5))

        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertForbidden(response)

    def test_forbid_create_by_non_project_client(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        non_project_client = self._get_client(~Q(project=5))

        self.force_login_user(non_project_client.pk)
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertForbidden(response)

    def test_unauthorized_create(self):
        creation_data = self.load_request_fixture('/floor_plans/create_floor_plan.json')
        response = self.client.post('/api/projects/5/floor-plans/', creation_data)

        self.assertUnauthorized(response)

    # Test update.
    def test_update_by_superuser(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        fixture_path = f'{self.requests_fixtures_dir}/media/test.pdf'
        new_media = {'file': self.load_pdf_fixture(fixture_path)}

        self._log_in_as_superuser()
        media_response = self.client.post('/api/media/', new_media, format='multipart')
        update_data['media'] = media_response.json()['id']

        floor_plan_id = 1

        response = self.client.put(f'/api/projects/5/floor-plans/{floor_plan_id}/', update_data)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': floor_plan_id, 'project': 5, **update_data})
        self.assertDatabaseHas(FloorPlanImage, {'plan_id': update_data['media']})

    def test_update_by_company_admin(self):
        fixture_path = f'{self.requests_fixtures_dir}/floor_plans/test.pdf'
        self.load_and_save_fake_pdf(path=fixture_path, name='broom.pdf')
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        company_admin = self._get_company_admin()

        self.force_login_user(company_admin.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': 1, 'project': 5, **update_data})
        self.assertDatabaseMissing(FloorPlanAreaPin, {'floor_plan_area__floor_plan': 1})

    def test_update_file_and_keep_pins(self):
        fixture_path = f'{self.requests_fixtures_dir}/floor_plans/test.pdf'
        self.load_and_save_fake_pdf(path=fixture_path, name='broom.pdf')
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan_without_deleting_pins.json')

        self._log_in_as_superuser()
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertOk(response)
        del update_data['keep_floor_plan_areas_and_floor_plan_pins']
        self.assertDatabaseHas(FloorPlan, {'pk': 1, 'project': 5, **update_data})
        self.assertDatabaseHas(FloorPlanAreaPin, {'floor_plan_area__floor_plan': 1})

    def test_update_by_project_admin(self):
        fixture_path = f'{self.requests_fixtures_dir}/floor_plans/test.pdf'
        self.load_and_save_fake_pdf(path=fixture_path, name='broom.pdf')
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        project_admin = self._get_admin(project=5)

        self.force_login_user(project_admin.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': 1, 'project': 5, **update_data})

    def test_update_by_project_manager(self):
        fixture_path = f'{self.requests_fixtures_dir}/floor_plans/test.pdf'
        self.load_and_save_fake_pdf(path=fixture_path, name='broom.pdf')
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        project_manager = self._get_manager(project=5)

        self.force_login_user(project_manager.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': 1, 'project': 5, **update_data})

    def test_forbid_update_by_non_project_admin(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        non_project_admin = self._get_admin(~Q(project=5))

        self.force_login_user(non_project_admin.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_non_project_manager(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        non_project_manager = self._get_manager(~Q(project=5))

        self.force_login_user(non_project_manager.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_project_consultant(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        project_consultant = self._get_consultant(project=5)

        self.force_login_user(project_consultant.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_project_subcontractor(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        project_subcontractor = self._get_subcontractor(project=5)

        self.force_login_user(project_subcontractor.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_project_client(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        project_client = self._get_client(project=5)

        self.force_login_user(project_client.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_non_project_consultant(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        non_project_consultant = self._get_consultant(~Q(project=5))

        self.force_login_user(non_project_consultant.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_non_project_subcontractor(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        non_project_subcontractor = self._get_subcontractor(~Q(project=5))

        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertForbidden(response)

    def test_forbid_update_by_non_project_client(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        non_project_client = self._get_client(~Q(project=5))

        self.force_login_user(non_project_client.pk)
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        response = self.client.put('/api/projects/5/floor-plans/1/', update_data)

        self.assertUnauthorized(response)

    # Test delete.

    def test_delete_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlan, 2)

    def test_delete_by_company_admin(self):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlan, 2)

    def test_delete_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlan, 2)

    def test_delete_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlan, 2)

    def test_forbid_delete_by_non_project_admin(self):
        non_project_admin = self._get_admin(~Q(project=5))
        self.force_login_user(non_project_admin.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertForbidden(response)

    def test_forbid_delete_by_non_project_manager(self):
        non_project_manager = self._get_manager(~Q(project=5))
        self.force_login_user(non_project_manager.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertForbidden(response)

    def test_forbid_delete_by_project_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertForbidden(response)

    def test_forbid_delete_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertForbidden(response)

    def test_forbid_delete_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertForbidden(response)

    def test_forbid_delete_by_non_project_consultant(self):
        non_project_consultant = self._get_consultant(~Q(project=5))
        self.force_login_user(non_project_consultant.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertForbidden(response)

    def test_forbid_delete_by_non_project_subcontractor(self):
        non_project_subcontractor = self._get_subcontractor(~Q(project=5))
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertForbidden(response)

    def test_forbid_delete_by_non_project_client(self):
        non_project_client = self._get_client(~Q(project=5))
        self.force_login_user(non_project_client.pk)
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/projects/5/floor-plans/2/')

        self.assertUnauthorized(response)

    # Test retrieve.

    def test_retrieve_with_expandable(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/', {'expand': ['expanded_package', 'expanded_media', 'expanded_image']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/retrieve_expanded_floor_plan.json')

    def test_retrieve_by_superuser(self):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/retrieve_floor_plan.json')

    def test_retrieve_by_company_admin(self):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/retrieve_floor_plan.json')

    def test_retrieve_by_project_admin(self):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/retrieve_floor_plan.json')

    def test_retrieve_by_project_manager(self):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/retrieve_floor_plan.json')

    def test_retrieve_by_project_consultant(self):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/retrieve_floor_plan.json')

    def test_retrieve_by_project_subcontractor(self):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/retrieve_floor_plan.json')

    def test_retrieve_by_project_client(self):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/retrieve_floor_plan.json')

    def test_forbid_retrieve_by_non_project_admin(self):
        non_project_admin = self._get_admin(~Q(project=5))
        self.force_login_user(non_project_admin.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_manager(self):
        non_project_manager = self._get_manager(~Q(project=5))
        self.force_login_user(non_project_manager.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_consultant(self):
        non_project_consultant = self._get_consultant(~Q(project=5))
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_subcontractor(self):
        non_project_subcontractor = self._get_subcontractor(~Q(project=5))
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertForbidden(response)

    def test_forbid_retrieve_by_non_project_client(self):
        non_project_client = self._get_client(~Q(project=5))
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertForbidden(response)

    def test_unauthorized_retrieve(self):
        response = self.client.get('/api/projects/5/floor-plans/1/')

        self.assertUnauthorized(response)

    # Test search.

    def get_filters(self):
        return (
            (
                {'all': True, 'sort': 'building,level'},
                '/floor_plans/list_all_floor_plans.json',
            ),
            (
                {'all': True, 'sort': 'building,level', 'package': [4]},
                '/floor_plans/filter_floor_plans_by_package.json',
            ),
            (
                {'all': True, 'sort': 'building,level', 'building': ['building1', 'building2']},
                '/floor_plans/filter_floor_plans_by_building.json',
            ),
            (
                {'all': True, 'sort': 'building,level', 'level': ['level1', 'level3']},
                '/floor_plans/filter_floor_plans_by_level.json',
            ),
            (
                {'all': True, 'area': ['fly']},
                '/floor_plans/filter_floor_plans_by_area.json',
            ),
            (
                {'all': True, 'has_floor_plan_area': True},
                '/floor_plans/filter_floor_plans_by_area_existence.json',
            ),
        )

    @data_provider(get_filters)
    def test_search_by_superuser(self, filters, fixture):
        superuser = self._get_superuser()
        self.force_login_user(superuser.pk)
        response = self.client.get('/api/projects/5/floor-plans/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_company_admin(self, filters, fixture):
        company_admin = self._get_company_admin()
        self.force_login_user(company_admin.pk)
        response = self.client.get('/api/projects/5/floor-plans/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_project_admin(self, filters, fixture):
        project_admin = self._get_admin(project=5)
        self.force_login_user(project_admin.pk)
        response = self.client.get('/api/projects/5/floor-plans/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_project_manager(self, filters, fixture):
        project_manager = self._get_manager(project=5)
        self.force_login_user(project_manager.pk)
        response = self.client.get('/api/projects/5/floor-plans/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_project_consultant(self, filters, fixture):
        project_consultant = self._get_consultant(project=5)
        self.force_login_user(project_consultant.pk)
        response = self.client.get('/api/projects/5/floor-plans/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_project_subcontractor(self, filters, fixture):
        project_subcontractor = self._get_subcontractor(project=5)
        self.force_login_user(project_subcontractor.pk)
        response = self.client.get('/api/projects/5/floor-plans/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_search_by_project_client(self, filters, fixture):
        project_client = self._get_client(project=5)
        self.force_login_user(project_client.pk)
        response = self.client.get('/api/projects/5/floor-plans/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_forbid_search_by_non_project_admin(self):
        non_project_admin = self._get_admin(~Q(project=5))
        self.force_login_user(non_project_admin.pk)
        response = self.client.get('/api/projects/5/floor-plans/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_manager(self):
        non_project_manager = self._get_manager(~Q(project=5))
        self.force_login_user(non_project_manager.pk)
        response = self.client.get('/api/projects/5/floor-plans/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_consultant(self):
        non_project_consultant = self._get_consultant(~Q(project=5))
        self.force_login_user(non_project_consultant.pk)
        response = self.client.get('/api/projects/5/floor-plans/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_subcontractor(self):
        non_project_subcontractor = self._get_subcontractor(~Q(project=5))
        self.force_login_user(non_project_subcontractor.pk)
        response = self.client.get('/api/projects/5/floor-plans/')

        self.assertForbidden(response)

    def test_forbid_search_by_non_project_client(self):
        non_project_client = self._get_client(~Q(project=5))
        self.force_login_user(non_project_client.pk)
        response = self.client.get('/api/projects/5/floor-plans/')

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/projects/5/floor-plans/')

        self.assertUnauthorized(response)

    def get_filters_for_quality_issue_plans(self):
        return (
            (
                {'all': True, 'status': ['in_progress'], 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_status.json'
            ),
            (
                {'all': True, 'except_status': [
                    'in_progress',
                    'requesting_approval',
                    'under_review',
                ], 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_excepted_status.json'
            ),
            (
                {'all': True, 'building': ['Building A'], 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_building.json'
            ),
            (
                {'all': True, 'level': ['7A'], 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_level.json'
            ),
            (
                {'all': True, 'area': ['fly'], 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_area.json'
            ),
            (
                {'all': True, 'id': [1], 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_floor_plan.json'
            ),
            (
                {'all': True, 'floor_plan_area': [2], 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_floor_plan_area.json'
            ),
            (
                {'all': True, 'user': [2], 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_user.json'
            ),
            (
                {'all': True, 'created_at__gte': '2020-09-23', 'created_at__lte': '2020-09-25', 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_created_at.json'
            ),
            (
                {'all': True, 'updated_at__gte': '2020-10-01', 'updated_at__lte': '2020-10-03', 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_updated_at.json'
            ),
            (
                {'all': True, 'subtask_is_defect': True, 'sort': 'id'},
                '/floor_plans/filter_by_quality_issue_related_subtask_is_defect.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True},
                '/floor_plans/filter_by_floor_area_pins_existence.json'
            ),
        )

    @data_provider(get_filters_for_quality_issue_plans)
    def test_list_for_quality_issue_by_superuser(self, filters: dict, fixture: str):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_list_for_quality_issue_by_company_admin(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_company_admin()
        response = self.client.get(url, {'all': True})

        self.assertOk(response)

    def test_list_for_quality_issue_by_project_admin(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertOk(response)

    def test_list_for_quality_issue_by_project_manager(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertOk(response)

    def test_list_for_quality_issue_by_project_client(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/get_all_for_quality_issue_by_client.json')

    def test_list_for_quality_issue_by_project_consultant(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plans/get_all_for_quality_issue_by_consultant.json')

    def test_forbid_list_for_quality_issue_by_project_subcontractor(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_admin(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_manager(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_client(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_consultant(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_subcontractor(self):
        url = reverse('floor_plan_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def get_filter_for_subtask_plans(self):
        return (
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'building': ['building1'], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_building.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'level': ['level1'], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_level.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'area': ['fly'], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_area.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'status': ['closed'], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_status.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'id': [1], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_floor_plan.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'package': [4], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_package.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'package_activity': [2], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_package_activity.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'package_activity_task': [2], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_package_activity_task.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'floor_plan_area': [1], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_floor_plan_area.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'user': [2], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_user.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'except_status': ['in_progress'], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_exclude_status.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'quality_issue': [1], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_quality_issue.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'is_defect': True, 'sort': 'id'},
                '/floor_plans/filter_by_subtask_is_defect.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'company': [3], 'sort': 'id'},
                '/floor_plans/filter_by_subtask_company.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'created_at__gte': '2020-07-31', 'created_at__lte': '2020-08-02', 'sort': 'id'},
                '/floor_plans/filter_by_subtask_created_at.json'
            ),
            (
                {'all': True, 'has_floor_plan_area_pins': True, 'updated_at__gte': '2020-07-31', 'updated_at__lte': '2020-08-04', 'sort': 'id'},
                '/floor_plans/filter_by_subtask_updated_at.json'
            ),
        )

    @data_provider(get_filter_for_subtask_plans)
    def test_list_for_subtask_by_superuser(self, filters: dict, fixture: str):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_list_for_subtask_by_company_admin(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_company_admin()
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_list_for_subtask_by_project_admin(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_list_for_subtask_by_project_manager(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_list_for_subtask_by_project_subcontractor(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_list_for_subtask_by_project_client(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_forbid_list_for_subtask_by_project_consultant(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_admin(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_manager(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_client(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_consultant(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_subcontractor(self):
        url = reverse('floor_plan_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_sync_location_matrix_by_project_staff_in_edit_mode(self):
        sync_data = self.load_request_fixture('/floor_plans/sync_location_matrix.json')

        self._log_in_as_staff(editmode__project=5)
        response = self.client.post('/api/projects/5/location-matrix/sync/', sync_data)

        self.assertOk(response)

        self.assertDatabaseMissing(FloorPlan, {'id': 1, 'building': 'Building A', 'level': '7A'})
        self.assertDatabaseHas(FloorPlan, {'id': 1, 'building': 'Building A', 'level': '6A'})
        self.assertDatabaseMissing(FloorPlanArea, {'id': 2, 'area': 'fly'})
        self.assertDatabaseHas(FloorPlanArea, {'id': 2, 'area': 'Hall'})
