from django.dispatch import receiver
from django_rest_passwordreset.models import ResetPasswordToken
from safedelete.signals import post_undelete

from api.mails.user.set_password import SetPassword
from api.models import User


@receiver(post_undelete, sender=User)
def user_post_undelete(sender, **kwargs):
    def create_token(user):
        return ResetPasswordToken.objects.create(user=user)

    instance = kwargs['instance']
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
