from django.conf import settings

from api.mails import Mail


class TaskSummaryCompanyAdminManagerAdmin(Mail):
    template_name = 'emails/summaries/company_admin_admin_manager_quality_critical_tasks.html'
    from_email = settings.GLOBAL_ADMIN_EMAIL
    from_name = settings.GLOBAL_ADMIN_EMAIL_NAME


class ReworkAndDefectsSummaryCompanyAdminManagerAdmin(Mail):
    template_name = 'emails/summaries/company_admin_admin_manager_rework_and_defects.html'
    from_email = settings.GLOBAL_ADMIN_EMAIL
    from_name = settings.GLOBAL_ADMIN_EMAIL_NAME
