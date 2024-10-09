from django.conf import settings

from api.mails import Mail


class QualityIssueCreated(Mail):
    template_name = 'emails/quality_issue/created.html'
    from_email = settings.GLOBAL_ADMIN_EMAIL
    subject = 'Quality Issue created'
    from_name = settings.GLOBAL_ADMIN_EMAIL_NAME
