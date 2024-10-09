from django.urls import reverse

from api.models import AppSettings
from api.tests.test import TestCase


class AppSettingsTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/user.json']

    def test_get_app_settings(self):
        self._log_in_as_superuser()
        response = self.client.get(reverse('app-settings'))

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/app_settings/get_app_settings.json')
        self.assertEqual(AppSettings.objects.count(), 1)

    def test_update_disable_user_registration_from_mobile_devices(self):
        data_to_update = self.load_request_fixture('/app_settings/update_disable_user_registration_from_mobile_devices.json')

        self._log_in_as_superuser()
        response = self.client.put(reverse('app-settings'), data=data_to_update)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/app_settings/update_disable_user_registration_from_mobile_devices.json')
        self.assertDatabaseHas(AppSettings, {'disable_user_registration_from_mobile_devices': True})
        self.assertEqual(AppSettings.objects.count(), 1)

    def test_forbid_update_app_settings(self):
        data_to_update = self.load_request_fixture('/app_settings/update_disable_user_registration_from_mobile_devices.json')

        self._log_in_as_admin()
        response = self.client.put(reverse('app-settings'), data=data_to_update)

        self.assertForbidden(response)

    def test_check_pre_register_settings(self):
        response = self.client.get(reverse('users-check_pre_register_settings'))

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/app_settings/check_pre_register_setting.json')
        self.assertDatabaseHas(AppSettings, {'disable_user_registration_from_mobile_devices': False})
        self.assertEqual(AppSettings.objects.count(), 1)
