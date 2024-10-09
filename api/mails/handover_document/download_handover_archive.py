from django.conf import settings

from api.mails import Mail


class DownloadHandoverArchive(Mail):
    template_name = 'emails/handover_document/download_handover_archive.html'
    from_email = settings.EMAIL_SUPPORT_EMAIL
    from_name = settings.EMAIL_SUPPORT_NAME
