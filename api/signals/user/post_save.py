from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.models import ResetPasswordToken

from api.mails.user.set_password import SetPassword
from api.models import User


@receiver(post_save, sender=User)
def user_post_save(sender, instance, **kwargs):
    def create_token(user):
        return ResetPasswordToken.objects.create(user=user)

    if kwargs.get('created', True) and not kwargs.get('raw', False) and instance.send_registration_emails:
        token = create_token(instance)
        context = {
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'token': token.key
        }

        return SetPassword() \
            .set_to(instance.email) \
            .set_context(context) \
            .send()
