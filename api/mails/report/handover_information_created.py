from django.conf import settings

from api.mails import Mail


class HandoverInformationReportCreated(Mail):
    template_name = 'emails/report/handover_information_created.html'
    from_email = settings.EMAIL_SUPPORT_EMAIL
    from_name = settings.EMAIL_SUPPORT_NAME
