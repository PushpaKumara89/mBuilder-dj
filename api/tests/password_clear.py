import pendulum
from django.core import management
from django_rest_passwordreset.models import ResetPasswordToken

from api.tests.test import TestCase


class PasswordClearTests(TestCase):
    fixtures = ['api/tests/fixtures/dumps/password_clear.json']

    def test_clear(self):
        pendulum.set_test_now(pendulum.datetime(2020, 7, 31, 11, 00))

        management.call_command('clear_expired_reset_password_tokens')

        self.assertDatabaseMissing(ResetPasswordToken, {'user_id': 2})
        self.assertDatabaseHas(ResetPasswordToken, {'user_id': 4})
        self.assertDatabaseHas(ResetPasswordToken, {'user_id': 3})

        pendulum.set_test_now(pendulum.datetime(2020, 2, 2))

    def test_clear_with_empty_password(self):
        pendulum.set_test_now(pendulum.datetime(2020, 9, 30, 11, 00))

        management.call_command('clear_expired_reset_password_tokens')

        self.assertDatabaseMissing(ResetPasswordToken, {'user_id': 2})
        self.assertDatabaseMissing(ResetPasswordToken, {'user_id': 4})
        self.assertDatabaseMissing(ResetPasswordToken, {'user_id': 3})

        pendulum.set_test_now(pendulum.datetime(2020, 2, 2))
