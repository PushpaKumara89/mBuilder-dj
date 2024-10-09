from unittest import mock

from django.core.files.storage import FileSystemStorage
from rest_framework.reverse import reverse

from api.models import Media
from api.tests.test import TestCase


class FloorPlanAreaPinThumbnailTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/floor_plan_area_pin_thumbnail.json']
    WORKING_PROJECT = 5
    fss = FileSystemStorage()

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_create_with_subtask_by_superuser(self):
        self.generate_and_save_fake_image('broom.png')

        new_temp_pin_thumbnail = self.load_request_fixture('/floor_plan_area_pin_thumbnail/create_temporary_thumbnail.json')
        url = reverse('floor_plan_area_pin_thumbnail-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 2
        })
        self._log_in_as_superuser()
        response = self.client.post(url, new_temp_pin_thumbnail)

        self.assertCreated(response)

        self.assertDatabaseHas(Media, {
            'is_public': False,
            'name__startswith': 'temp-pin-thumb'
        })

        self.assertEquals(Media.objects.filter(
            is_public=False,
            name__startswith='temp-pin-thumb'
        ).count(), 2)

    @mock.patch('api.storages.AzureMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @mock.patch('api.storages.AzureMediaStorage.save', fss.save)
    @mock.patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_create_with_subtask_by_project_user(self):
        self.generate_and_save_fake_image('broom.png')

        new_temp_pin_thumbnail = self.load_request_fixture('/floor_plan_area_pin_thumbnail/create_temporary_thumbnail.json')
        url = reverse('floor_plan_area_pin_thumbnail-list', kwargs={
            'project_pk': self.WORKING_PROJECT,
            'pk': 2
        })
        self._log_in_as_user(project=self.WORKING_PROJECT)
        response = self.client.post(url, new_temp_pin_thumbnail)

        self.assertCreated(response)

        self.assertDatabaseHas(Media, {
            'is_public': False,
            'name__startswith': 'temp-pin-thumb'
        })

        self.assertEquals(Media.objects.filter(
            is_public=False,
            name__startswith='temp-pin-thumb'
        ).count(), 2)
