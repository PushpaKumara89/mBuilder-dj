from django.conf import settings

from api.mails import Mail


class DownloadMultipleHandoverDocumentFiles(Mail):
    subject = 'Handover Information Report - Archive of selected files'
    template_name = 'emails/handover_document/download_multiple_files.html'
    from_email = settings.EMAIL_SUPPORT_EMAIL
    from_name = settings.EMAIL_SUPPORT_NAME
