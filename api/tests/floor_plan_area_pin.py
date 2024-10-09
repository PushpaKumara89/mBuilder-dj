from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from rest_framework.reverse import reverse

from api.models import Subtask, FloorPlanAreaPin, QualityIssue, QualityIssueUpdate, SubtaskUpdate, \
    FloorPlanAreaPinThumbnail
from api.tests.test import TestCase, data_provider


class FloorPlanAreaPinTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/floor_plan_area_pin.json']
    WORKING_PROJECT = 5
    fss = FileSystemStorage()

    def test_get_subtask_with_pins(self):
        self._log_in_as_superuser()
        response = self.client.get(reverse('subtasks_detail', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': 1}), {'expand': ['expanded_floor_plan_area_pin']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area_pin/get_subtask_with_pins.json')

    def test_get_quality_issue_with_pins(self):
        self._log_in_as_superuser()
        response = self.client.get(reverse('quality_issue_detail', kwargs={'project_pk': self.WORKING_PROJECT, 'pk': 1}), {'expand': ['expanded_floor_plan_area_pin']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area_pin/get_quality_issue_with_pins.json')

    def test_update_with_quality_issue_by_superuser(self):
        self.generate_and_save_fake_image('broom.png')

        content_type = ContentType.objects.get_for_model(QualityIssue)
        new_quality_issue_update = self.load_request_fixture('/floor_plan_area_pin/new_quality_issue_update.json')
        url = reverse('quality_issue_update_list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'quality_issue_pk': 1
        })
        self._log_in_as_superuser()
        response = self.client.post(url, new_quality_issue_update)

        self.assertCreated(response)

        pin = new_quality_issue_update['new_data']['floor_plan_area_pin']
        self.assertDatabaseHas(QualityIssueUpdate, {
            'comment': new_quality_issue_update['comment'],
            'new_data__status': new_quality_issue_update['new_data']['status'],
            'new_data__description': new_quality_issue_update['new_data']['description'],
            'new_data__floor_plan_area_pin__pin': new_quality_issue_update['new_data']['floor_plan_area_pin']['pin'],
            'new_data__floor_plan_area_pin__id': new_quality_issue_update['new_data']['floor_plan_area_pin']['id'],
        })
        self.assertDatabaseHas(
            QualityIssue, {'pk': 1, 'status': new_quality_issue_update['new_data']['status'], 'user__pk': 1}
        )
        self.assertDatabaseHas(FloorPlanAreaPin, {
            'content_type': content_type,
            **pin
        })

    def test_delete_with_quality_issue_update_by_superuser(self):
        content_type = ContentType.objects.get_for_model(QualityIssue)
        new_quality_issue_update = self.load_request_fixture('/floor_plan_area_pin/delete_from_quality_issue_update.json')
        url = reverse('quality_issue_update_list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'quality_issue_pk': 1
        })
        self._log_in_as_superuser()
        response = self.client.post(url, new_quality_issue_update)

        self.assertCreated(response)

        self.assertDatabaseHas(QualityIssueUpdate, {
            'comment': new_quality_issue_update['comment'],
            'new_data__status': new_quality_issue_update['new_data']['status'],
            'new_data__floor_plan_area_pin': None
        })
        self.assertDatabaseMissing(FloorPlanAreaPin, {
            'content_type': content_type,
            'object_id': 1
        })

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_update_with_subtask_by_superuser(self):
        self.generate_and_save_fake_image('broom.png')

        content_type = ContentType.objects.get_for_model(Subtask)
        new_subtask_update = self.load_request_fixture('/floor_plan_area_pin/new_subtask_update.json')
        url = reverse('subtasks_updates_list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'subtask_pk': 1
        })
        self._log_in_as_superuser()
        response = self.client.post(url, new_subtask_update)

        self.assertCreated(response)

        pin = new_subtask_update['new_data']['floor_plan_area_pin']
        self.assertDatabaseHas(SubtaskUpdate, {
            'comment': new_subtask_update['comment'],
            'new_data__status': new_subtask_update['new_data']['status'],
            'new_data__description': new_subtask_update['new_data']['description'],
            'new_data__floor_plan_area_pin__pin': new_subtask_update['new_data']['floor_plan_area_pin']['pin'],
            'new_data__floor_plan_area_pin__id': new_subtask_update['new_data']['floor_plan_area_pin']['id'],
        })
        self.assertDatabaseHas(
            Subtask, {'pk': 1, 'status': new_subtask_update['new_data']['status']}
        )
        self.assertDatabaseHas(FloorPlanAreaPin, {
            'content_type': content_type,
            **pin
        })
        self.assertDatabaseMissing(FloorPlanAreaPinThumbnail, 1)
        self.assertDatabaseHas(FloorPlanAreaPinThumbnail, {'floor_plan_area_pin': 1})
        self.assertEquals(
            FloorPlanAreaPinThumbnail.objects.filter(floor_plan_area_pin=1).count(),
            2
        )

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_create_with_subtask_by_superuser(self):
        self.generate_and_save_fake_image('broom.png')

        content_type = ContentType.objects.get_for_model(Subtask)
        new_subtask_update = self.load_request_fixture('/floor_plan_area_pin/create_with_subtask_update.json')
        url = reverse('subtasks_updates_list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'subtask_pk': 7
        })
        self._log_in_as_superuser()
        response = self.client.post(url, new_subtask_update)

        self.assertCreated(response)

        pin = new_subtask_update['new_data']['floor_plan_area_pin']
        self.assertDatabaseHas(SubtaskUpdate, {
            'comment': new_subtask_update['comment'],
            'new_data__status': new_subtask_update['new_data']['status'],
            'new_data__floor_plan_area_pin__pin': new_subtask_update['new_data']['floor_plan_area_pin']['pin'],
        })
        self.assertDatabaseHas(FloorPlanAreaPin, {
            'content_type': content_type,
            **pin
        })
        self.assertDatabaseHas(FloorPlanAreaPinThumbnail, {
            'floor_plan_area_pin__object_id': 7,
            'floor_plan_area_pin__content_type': content_type
        })
        self.assertEquals(
            FloorPlanAreaPinThumbnail.objects.filter(
                floor_plan_area_pin__object_id=7,
                floor_plan_area_pin__content_type=content_type,
            ).count(),
            2
        )

    def test_delete_with_subtask_update_by_superuser(self):
        content_type = ContentType.objects.get_for_model(Subtask)
        new_subtask_update = self.load_request_fixture('/floor_plan_area_pin/delete_from_subtask_update.json')
        url = reverse('subtasks_updates_list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'subtask_pk': 1
        })
        self._log_in_as_superuser()
        response = self.client.post(url, new_subtask_update)

        self.assertCreated(response)

        self.assertDatabaseHas(SubtaskUpdate, {
            'comment': new_subtask_update['comment'],
            'new_data__status': new_subtask_update['new_data']['status'],
            'new_data__floor_plan_area_pin': None
        })
        self.assertDatabaseMissing(FloorPlanAreaPin, {
            'content_type': content_type,
            'object_id': 1
        })

    def get_filter_for_subtask_pins(self):
        return (
            (
                {'all': True, 'building': ['building1'], 'order': 'id'},
                '/floor_plan_area_pin/filter_by_subtask_building.json'
            ),
            (
                {'all': True, 'level': ['level1'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_level.json'
            ),
            (
                {'all': True, 'area': ['beatle'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_area.json'
            ),
            (
                {'all': True, 'status': ['closed'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_status.json'
            ),
            (
                {'all': True, 'floor_plan': [1], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_floor_plan.json'
            ),
            (
                {'all': True, 'package': [4], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_package.json'
            ),
            (
                {'all': True, 'package_activity': [2], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_package_activity.json'
            ),
            (
                {'all': True, 'package_activity_task': [2], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_package_activity_task.json'
            ),
            (
                {'all': True, 'object_id': 2, 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_object_id.json'
            ),
            (
                {'all': True, 'floor_plan_area': [1], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_floor_plan_area.json'
            ),
            (
                {'all': True, 'user': [2], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_user.json'
            ),
            (
                {'all': True, 'except_status': ['removed'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_exclude_status.json'
            ),
            (
                {'all': True, 'quality_issue': [1], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_quality_issue.json'
            ),
            (
                {'all': True, 'is_defect': True, 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_is_defect.json'
            ),
            (
                {'all': True, 'company': [3], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_company.json'
            ),
            (
                {'all': True, 'created_at__gte': '2020-07-31', 'created_at__lte': '2020-08-02', 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_created_at.json'
            ),
            (
                {'all': True, 'updated_at__gte': '2020-07-31', 'updated_at__lte': '2020-08-04', 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_subtask_updated_at.json'
            ),
            (
                {'all': True, 'expand': ['expanded_object_id.expanded_task', 'expanded_subtask.expanded_task', 'expanded_thumbnails.expanded_thumbnail'], 'sort': 'object_id'},
                '/floor_plan_area_pin/get_with_expanded_for_subtask.json'
            ),
        )

    @data_provider(get_filter_for_subtask_pins)
    def test_list_for_subtask_by_superuser(self, filters: dict, fixture: str):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_list_for_subtask_by_company_admin(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_company_admin()
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_list_for_subtask_by_project_admin(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_list_for_subtask_by_project_manager(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_list_for_subtask_by_project_subcontractor(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_list_for_subtask_by_project_client(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertOk(response)

    def test_forbid_list_for_subtask_by_project_consultant(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_admin(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_manager(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_client(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_consultant(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def test_forbid_list_for_subtask_by_non_project_subcontractor(self):
        url = reverse('floor_plan_area_subtask-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all:': True})

        self.assertForbidden(response)

    def get_filters_for_quality_issue_pins(self):
        return (
            (
                {'all': True, 'status': ['in_progress'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_status.json'
            ),
            (
                {'all': True, 'except_status': ['in_progress'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_excepted_status.json'
            ),
            (
                {'all': True, 'building': ['building1'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_building.json'
            ),
            (
                {'all': True, 'level': ['level1'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_level.json'
            ),
            (
                {'all': True, 'area': ['beatle'], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_area.json'
            ),
            (
                {'all': True, 'object_id': 2, 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_object_id.json'
            ),
            (
                {'all': True, 'floor_plan': [2], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_floor_plan.json'
            ),
            (
                {'all': True, 'floor_plan_area': [1], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_floor_plan_area.json'
            ),
            (
                {'all': True, 'user': [2], 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_user.json'
            ),
            (
                {'all': True, 'created_at__gte': '2020-09-23', 'created_at__lte': '2020-09-25', 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_created_at.json'
            ),
            (
                {'all': True, 'updated_at__gte': '2020-10-01', 'updated_at__lte': '2020-10-03', 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_updated_at.json'
            ),
            (
                {'all': True, 'subtask_is_defect': True, 'sort': 'object_id'},
                '/floor_plan_area_pin/filter_by_quality_issue_related_subtask_is_defect.json'
            ),
            (
                {'all': True, 'expand': ['expanded_object_id.expanded_location_matrix', 'expanded_quality_issue.expanded_location_matrix', 'expanded_thumbnails.expanded_thumbnail'], 'sort': 'object_id'},
                '/floor_plan_area_pin/get_with_expanded_for_quality_issue.json'
            ),
        )

    @data_provider(get_filters_for_quality_issue_pins)
    def test_list_for_quality_issue_by_superuser(self, filters: dict, fixture: str):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_superuser()
        response = self.client.get(url, filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_list_for_quality_issue_by_company_admin(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_company_admin()
        response = self.client.get(url, {'all': True})

        self.assertOk(response)

    def test_list_for_quality_issue_by_project_admin(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_admin(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertOk(response)

    def test_list_for_quality_issue_by_project_manager(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_manager(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertOk(response)

    def test_list_for_quality_issue_by_project_client(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_client(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area_pin/get_all_for_quality_issue_by_client.json')

    def test_list_for_quality_issue_by_project_consultant(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_consultant(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/floor_plan_area_pin/get_all_for_quality_issue_by_consultant.json')

    def test_forbid_list_for_quality_issue_by_project_subcontractor(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_subcontractor(project=self.WORKING_PROJECT)
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_admin(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_admin(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_manager(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_manager(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_client(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_client(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_consultant(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_consultant(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)

    def test_forbid_list_for_quality_issue_by_non_project_subcontractor(self):
        url = reverse('floor_plan_area_quality_issue-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
        })

        self._log_in_as_subcontractor(~Q(project=self.WORKING_PROJECT))
        response = self.client.get(url, {'all': True})

        self.assertForbidden(response)
