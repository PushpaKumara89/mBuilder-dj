from django.conf import settings

from api.mails import Mail


class SubtaskStatusChanged(Mail):
    template_name = 'emails/subtask/status_changed.html'
    from_email = settings.GLOBAL_ADMIN_EMAIL
    from_name = settings.GLOBAL_ADMIN_EMAIL_NAME
