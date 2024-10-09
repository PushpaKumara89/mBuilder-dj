import pendulum as pendulum
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from django_rest_passwordreset.models import ResetPasswordToken


class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to clean out expired tokens"

    def handle(self, *args, **options):
        existing_user_expiry_time = pendulum.now().subtract(**self.__get_password_reset_token_expiry_time())
        new_user_expiry_time = pendulum.now().subtract(**self.__get_password_reset_token_expiry_time_for_new_user())

        self.__clear_expired(existing_user_expiry_time, new_user_expiry_time)

    def __clear_expired(self, existing_user_expiry_time, new_user_expiry_time):
        """
        Remove all expired tokens
        :param new_user_expiry_time: Token expiration time for new user without password
        :param existing_user_expiry_time: Token expiration time for existing user
        """
        existing_user_expired_token_query = (~Q(user__password__exact='') & Q(created_at__lte=existing_user_expiry_time))
        new_user_expired_token_query = (Q(user__password__exact='') & Q(created_at__lte=new_user_expiry_time))

        ResetPasswordToken.objects.filter(new_user_expired_token_query | existing_user_expired_token_query).delete()

    def __get_password_reset_token_expiry_time_for_new_user(self):
        return getattr(settings, 'RESET_TOKEN_EXPIRY_TIME_FOR_USER_WITHOUT_PASSWORD', {'months': 1})

    def __get_password_reset_token_expiry_time(self):
        return getattr(settings, 'RESET_TOKEN_EXPIRY_TIME_FOR_USER_WITH_PASSWORD', {'minutes': 30})
