from django.conf import settings

from api.mails import Mail


class TaskStatusChanged(Mail):
    template_name = 'emails/task/status_changed.html'
    from_email = settings.GLOBAL_ADMIN_EMAIL
    from_name = settings.GLOBAL_ADMIN_EMAIL_NAME
