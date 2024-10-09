from datetime import timedelta
from functools import partial
from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.utils import aware_utcnow

from api.models import EditMode
from api.tests.test import TestCase


class AuthTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/auth.json']

    login_url = reverse('token_obtain_pair')
    refresh_token_url = reverse('token_refresh')
    logout_url = reverse('api_logout')

    def _login(self):
        data = {
            'email': 'cool.brad@gmail.com', 'password': '123456Qwe-'
        }
        response = self.client.post(self.login_url, data)
        body = response.json()

        if 'access' in body:
            self.client.credentials(HTTP_AUTHORIZATION='Bearer %s' % body['access'])

        return response.status_code, body

    def test_logout(self):
        _, body = self._login()
        response = self.client.post(self.logout_url, {'refresh': body['refresh']})
        body = response.content

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(body)

        self.assertTrue(EditMode.objects.filter(user__email='cool.brad@gmail.com').exists())

    def test_logout_with_force_remove_edit_mode(self):
        _, body = self._login()
        response = self.client.post(self.logout_url, {'refresh': body['refresh'], 'force_remove_edit_mode': True})
        body = response.content

        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(body)

        self.assertFalse(EditMode.objects.filter(user__email='cool.brad@gmail.com').exists())

    def test_logout_with_bad_refresh_token(self):
        self._login()
        response = self.client.post(self.logout_url, {'refresh': 'dsf.sdfsdf.sdf'})
        body = response.json()

        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(body)

    def test_logout_refresh_token_in_blacklist(self):
        _, body = self._login()
        response = self.client.post(self.logout_url, body)
        token = partial(RefreshToken, body['refresh'])

        self.assertRaises(TokenError, token)

    def test_access_token_still_valid_after_logout(self):
        _, body = self._login()
        self.client.post(self.logout_url, body)

        response = self.client.get('/api/users/1/')
        body = response.json()

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertTrue(body)

    def test_access_token_invalid_in_hour_after_logout(self):
        _, body = self._login()
        self.client.post(self.logout_url, body)

        m = mock.Mock()
        m.return_value = aware_utcnow() + timedelta(minutes=1441)

        with mock.patch('rest_framework_simplejwt.tokens.aware_utcnow', m):
            response = self.client.get('/api/users/1/')
            body = response.json()

        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(body)
