from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.urls import reverse

from api.models import FloorPlan, FloorPlanArea, FloorPlanRevisionMeta
from api.models.floor_plan_revision import FloorPlanRevision
from api.tests.test import TestCase, data_provider


class FloorPlanRevisionTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/floor_plan_revisions.json',
    ]
    fss = FileSystemStorage()
    WORKING_PROJECT = 5

    def get_filters(self):
        return (
            (
                {'all': True, 'floor_plan': 1},
                '/floor_plan_revisions/get_filtered_by_floor_plan.json'
            ),
            (
                {'all': True, 'page': 2, 'per_page': 2},
                '/floor_plan_revisions/get_paginated.json'
            ),
            (
                {'all': True, 'expand': [
                    'expanded_meta',
                    'expanded_user',
                    'expanded_floor_plan.expanded_media',
                    'expanded_floor_plan_areas',
                ]},
                '/floor_plan_revisions/get_with_expanded.json'
            ),
        )

    @data_provider(get_filters)
    def test_list_by_superuser(self, filters: dict, fixture: str):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_list_by_company_admin(self, filters: dict, fixture: str):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_company_admin()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_list_by_project_admin(self, filters: dict, fixture: str):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    @data_provider(get_filters)
    def test_list_by_project_manager(self, filters: dict, fixture: str):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_list_by_project_client(self,):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_project_consultant(self,):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_project_subcontractor(self,):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_admin(self,):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_manager(self,):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_client(self,):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_consultant(self,):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_list_by_non_project_subcontractor(self,):
        url = reverse('floor_plan_revisions-list', kwargs={
            'project_pk': self.WORKING_PROJECT
        })
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_delete_floor_plan_area(self):
        floor_plan_area_content_type = ContentType.objects.get_for_model(FloorPlanArea)
        floor_plan_content_type = ContentType.objects.get_for_model(FloorPlan)
        deleting_floor_plan_area = 1

        floor_plan = FloorPlan.objects.filter(floorplanarea__id=deleting_floor_plan_area).get()
        floor_plan_revisions_count_before_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_content_type,
            version__object_id=floor_plan.id
        ).count()

        floor_plan_area_revisions_count_before_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_area_content_type,
            version__object_id=deleting_floor_plan_area
        ).count()

        last_floor_plan_meta_before_action = FloorPlanRevisionMeta.objects.order_by('-id').first()

        url = reverse('floor_plan_area_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': deleting_floor_plan_area
        })

        self._log_in_as_superuser()
        response = self.client.delete(url)

        self.assertNoContent(response)
        self.assertSoftDeleted(FloorPlanArea, deleting_floor_plan_area)

        # Make sure that revision was created for the FloorPlan
        floor_plan_revisions_count_after_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_content_type,
            version__object_id=floor_plan.id
        ).count()

        self.assertGreater(floor_plan_revisions_count_after_action, floor_plan_revisions_count_before_action)

        # Make sure that revision was created for the FloorPlanArea
        floor_plan_area_revisions_count_after_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_area_content_type,
            version__object_id=deleting_floor_plan_area
        ).count()

        self.assertGreater(floor_plan_area_revisions_count_after_action, floor_plan_area_revisions_count_before_action)

        # Make sure RevisionMeta was created with appropriate event type.
        last_floor_plan_meta_after_action = FloorPlanRevisionMeta.objects.order_by('-id').first()
        self.assertNotEquals(last_floor_plan_meta_before_action.id, last_floor_plan_meta_after_action.id)
        self.assertEquals(last_floor_plan_meta_after_action.event_type, FloorPlanRevisionMeta.EventTypes.AREAS_UPDATED.value)

    def test_change_floor_plan_media(self):
        floor_plan_area_content_type = ContentType.objects.get_for_model(FloorPlanArea)
        floor_plan_content_type = ContentType.objects.get_for_model(FloorPlan)
        updating_floor_plan = 1

        floor_plan = FloorPlan.objects.filter(id=updating_floor_plan).get()
        floor_plan_revisions_count_before_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_content_type,
            version__object_id=floor_plan.id
        ).count()

        floor_plan_areas_id = list(FloorPlanArea.objects.filter(floor_plan=updating_floor_plan).values_list('id', flat=True))
        floor_plan_area_revisions_count_before_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_area_content_type,
            version__object_id__in=floor_plan_areas_id
        ).count()

        last_floor_plan_meta_before_action = FloorPlanRevisionMeta.objects.order_by('-id').first()

        url = reverse('floor_plan_detail', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': updating_floor_plan
        })

        update_data = self.load_request_fixture('/floor_plans/update_floor_plan.json')
        self._log_in_as_superuser()

        response = self.client.put(url, update_data)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': updating_floor_plan, 'project': 5, **update_data})

        # Make sure that revision was created for the FloorPlan
        floor_plan_revisions_count_after_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_content_type,
            version__object_id=floor_plan.id
        ).count()

        self.assertGreater(floor_plan_revisions_count_after_action, floor_plan_revisions_count_before_action)

        # Make sure that revision was created for the FloorPlanArea
        floor_plan_area_revisions_count_after_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_area_content_type,
            version__object_id__in=floor_plan_areas_id
        ).count()

        self.assertGreater(floor_plan_area_revisions_count_after_action, floor_plan_area_revisions_count_before_action)

        # Make sure RevisionMeta was created with appropriate event type.
        last_floor_plan_meta_after_action = FloorPlanRevisionMeta.objects.order_by('-id').first()
        self.assertNotEquals(last_floor_plan_meta_before_action.id, last_floor_plan_meta_after_action.id)
        self.assertEquals(last_floor_plan_meta_after_action.event_type, FloorPlanRevisionMeta.EventTypes.FILE_UPDATED.value)

    def test_revert_floor_plan_revision_by_superuser(self):
        floor_plan_area_content_type = ContentType.objects.get_for_model(FloorPlanArea)
        floor_plan_content_type = ContentType.objects.get_for_model(FloorPlan)
        reverting_floor_plan_id = 1

        floor_plan = FloorPlan.objects.filter(id=reverting_floor_plan_id).get()
        floor_plan_revisions_count_before_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_content_type,
            version__object_id=floor_plan.id
        ).count()

        floor_plan_areas_id = list(FloorPlanArea.objects.filter(floor_plan=reverting_floor_plan_id).values_list('id', flat=True))
        floor_plan_area_revisions_count_before_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_area_content_type,
            version__object_id__in=floor_plan_areas_id
        ).count()

        last_floor_plan_meta_before_action = FloorPlanRevisionMeta.objects.order_by('-id').first()

        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_superuser()
        response = self.client.post(url)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': reverting_floor_plan_id, 'media': 2})

        # Make sure that revision was created for the FloorPlan
        floor_plan_revisions_count_after_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_content_type,
            version__object_id=floor_plan.id
        ).count()

        self.assertGreater(floor_plan_revisions_count_after_action, floor_plan_revisions_count_before_action)

        # Make sure that revision was created for the FloorPlanArea
        floor_plan_area_revisions_count_after_action = FloorPlanRevision.objects.filter(
            version__content_type=floor_plan_area_content_type,
            version__object_id__in=floor_plan_areas_id
        ).count()

        self.assertGreater(floor_plan_area_revisions_count_after_action, floor_plan_area_revisions_count_before_action)

        # Make sure RevisionMeta was created with appropriate event type.
        last_floor_plan_meta_after_action = FloorPlanRevisionMeta.objects.order_by('-id').first()
        self.assertNotEquals(last_floor_plan_meta_before_action.id, last_floor_plan_meta_after_action.id)
        self.assertEquals(last_floor_plan_meta_after_action.event_type, FloorPlanRevisionMeta.EventTypes.AREAS_UPDATED.value)

    def test_revert_floor_plan_revision_by_company_admin(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_company_admin()
        response = self.client.post(url)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': reverting_floor_plan_id, 'media': 2})

    def test_revert_floor_plan_revision_by_project_admin(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.post(url)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': reverting_floor_plan_id, 'media': 2})

    def test_revert_floor_plan_revision_by_project_manager(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.post(url)

        self.assertOk(response)
        self.assertDatabaseHas(FloorPlan, {'pk': reverting_floor_plan_id, 'media': 2})

    def test_revert_floor_plan_revision_by_project_client(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.post(url)

        self.assertForbidden(response)

    def test_revert_floor_plan_revision_by_project_consultant(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.post(url)

        self.assertForbidden(response)

    def test_revert_floor_plan_revision_by_project_subcontractor(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.post(url)

        self.assertForbidden(response)

    def test_revert_floor_plan_revision_by_non_project_admin(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url)

        self.assertForbidden(response)

    def test_revert_floor_plan_revision_by_non_project_manager(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url)

        self.assertForbidden(response)

    def test_revert_floor_plan_revision_by_non_project_client(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url)

        self.assertForbidden(response)

    def test_revert_floor_plan_revision_by_non_project_consultant(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url)

        self.assertForbidden(response)

    def test_revert_floor_plan_revision_by_non_project_subcontractor(self):
        reverting_floor_plan_id = 1
        url = reverse('floor_plan_revisions-revert', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'floor_plan_pk': reverting_floor_plan_id,
            'pk': 1
        })

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.post(url)

        self.assertForbidden(response)

    def test_retrieve_by_superuser(self):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_superuser()
        response = self.client.get(url, {'expand': [
            'expanded_meta',
            'expanded_user',
            'expanded_floor_plan.expanded_media',
            'expanded_floor_plan.expanded_image',
            'expanded_floor_plan.expanded_package',
            'expanded_floor_plan_areas'
        ]})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_revisions/retrieve_revision_by_superuser.json')

    def test_retrieve_by_company_admin(self):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_company_admin()
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_revisions/retrieve_revision.json')

    def test_retrieve_by_project_admin(self):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_revisions/retrieve_revision.json')

    def test_retrieve_by_project_manager(self):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_revisions/retrieve_revision.json')

    def test_retrieve_by_project_client(self,):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_project_consultant(self,):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_project_subcontractor(self,):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_admin(self,):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_manager(self,):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_client(self,):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_consultant(self,):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

    def test_retrieve_by_non_project_subcontractor(self,):
        url = reverse('floor_plan_revisions-retrieve', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 1
        })
        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url)

        self.assertForbidden(response)

