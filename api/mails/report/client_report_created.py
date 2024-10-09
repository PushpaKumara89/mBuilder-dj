from django.conf import settings

from api.mails import Mail


class ClientReportCreated(Mail):
    template_name = 'emails/report/client_report_created.html'
    from_email = settings.EMAIL_SUPPORT_EMAIL
    from_name = settings.EMAIL_SUPPORT_NAME
