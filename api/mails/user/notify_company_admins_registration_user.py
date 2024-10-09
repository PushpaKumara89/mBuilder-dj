from django.conf import settings
from django.utils.translation import gettext as _

from api.mails import Mail


class NotifyCompanyAdminsRegistrationUser(Mail):
    template_name = 'emails/user/notify_company_admins_registration_user.html'
    subject = _('A new user has been registered')
    from_email = settings.EMAIL_SUPPORT_EMAIL
