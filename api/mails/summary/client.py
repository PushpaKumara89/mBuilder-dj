from django.conf import settings

from api.mails import Mail


class SummaryClient(Mail):
    template_name = 'emails/summaries/client.html'
    from_email = settings.GLOBAL_ADMIN_EMAIL
    from_name = settings.GLOBAL_ADMIN_EMAIL_NAME
