from django.conf import settings
from django.utils.translation import gettext as _

from api.mails import Mail


class SetPassword(Mail):
    template_name = 'emails/user/set_password.html'
    subject = _('Your MBuild account has been created')
    from_email = settings.EMAIL_SUPPORT_EMAIL
