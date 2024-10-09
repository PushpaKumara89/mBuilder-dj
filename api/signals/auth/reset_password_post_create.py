from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from api.mails.user.password_reset import PasswordReset


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    context = {
        'first_name': reset_password_token.user.first_name,
        'last_name': reset_password_token.user.last_name,
        'token': reset_password_token.key,
        'email': reset_password_token.user.email
    }

    return PasswordReset() \
        .set_to(reset_password_token.user.email) \
        .set_context(context) \
        .send()
