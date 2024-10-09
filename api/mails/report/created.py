from django.conf import settings

from api.mails import Mail


class ReportCreated(Mail):
    template_name = 'emails/report/created.html'
    from_email = settings.EMAIL_SUPPORT_EMAIL
    from_name = settings.EMAIL_SUPPORT_NAME
