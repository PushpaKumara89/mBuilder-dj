from django.conf import settings

from api.mails import Mail


class SubtaskCommentCreated(Mail):
    template_name = 'emails/subtask/comment_created.html'
    from_email = settings.GLOBAL_ADMIN_EMAIL
    from_name = settings.GLOBAL_ADMIN_EMAIL_NAME
