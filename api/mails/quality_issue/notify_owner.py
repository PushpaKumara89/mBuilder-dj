from django.conf import settings

from api.mails import Mail


class QualityIssueStatusChanged(Mail):
    template_name = 'emails/quality_issue/status_changed.html'
    from_email = settings.GLOBAL_ADMIN_EMAIL
    from_name = settings.GLOBAL_ADMIN_EMAIL_NAME
