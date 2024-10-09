import pendulum
from django.db.models import Q

from api.enums import SummaryType
from api.mails.summary import SummaryClient, SummarySubcontractor, SummaryConsultant
from api.mails.summary.company_admin_manager_admin import ReworkAndDefectsSummaryCompanyAdminManagerAdmin, \
    TaskSummaryCompanyAdminManagerAdmin
from api.models import Project, User


def send_summary_for_client(project: Project, summary_type: SummaryType, counters: dict):
    to = list(
        project.projectuser_set.filter(
            user__group=User.Group.CLIENT.value,
            is_notifications_enabled=True
        ).all().values_list('user__email', flat=True)
    )

    summary_type = 'Weekly' \
        if summary_type == SummaryType.weekly \
        else 'Daily'

    SummaryClient(). \
        set_subject('MBuild %s Summary – Quality Issue Report: %s' % (summary_type, project.name,)). \
        set_to(to). \
        set_context(
        {
            **counters,
            'summary_type': summary_type,
            'project_name': project.name,
            'project_pk': project.pk,
            'today_date': pendulum.now()
        }). \
        send()


def send_summary_for_consultant(project: Project, summary_type: SummaryType, company_pk: int, counters: dict):
    to = list(
        project.projectuser_set.filter(
            user__group=User.Group.CONSULTANT.value,
            is_notifications_enabled=True,
            user__company=company_pk
        ).all().values_list('user__email', flat=True).distinct()
    )

    summary_type = 'Weekly' \
        if summary_type == SummaryType.weekly \
        else 'Daily'

    SummaryConsultant(). \
        set_subject('MBuild %s Summary – Quality Issue Report: %s' % (summary_type, project.name,)). \
        set_to(to). \
        set_context(
        {
            **counters,
            'summary_type': summary_type,
            'project_name': project.name,
            'project_pk': project.pk,
            'today_date': pendulum.now()
        }). \
        send()


def send_task_summary_for_company_admin_manager_admin(project: Project, summary_type: SummaryType, counters: dict):
    to = list(
        User.objects.filter(
            Q(groups=User.Group.COMPANY_ADMIN.value) |
            Q(
                projectuser__project=project,
                projectuser__is_notifications_enabled=True,
                groups__in=[
                    User.Group.ADMIN.value,
                    User.Group.MANAGER.value
                ]
            )
        ).distinct().values_list('email', flat=True)
    )

    summary_type = 'Weekly' \
        if summary_type == SummaryType.weekly \
        else 'Daily'

    TaskSummaryCompanyAdminManagerAdmin(). \
        set_subject('MBuild – Quality Critical Task %s Summary – %s' % (summary_type, project.name,)). \
        set_to(to). \
        set_context(
        {
            **counters,
            'summary_type': summary_type,
            'project_name': project.name,
            'project_pk': project.pk,
            'today_date': pendulum.now()
        }). \
        send()


def send_quality_issues_subtasks_summary_for_company_admin_manager_admin(project: Project, summary_type: SummaryType, counters: dict):
    to = list(
        User.objects.filter(
            Q(groups=User.Group.COMPANY_ADMIN.value) |
            Q(
                projectuser__project=project,
                projectuser__is_notifications_enabled=True,
                groups__in=[
                    User.Group.ADMIN.value,
                    User.Group.MANAGER.value
                ]
            )
        ).distinct().values_list('email', flat=True)
    )

    summary_type = 'Weekly' \
        if summary_type == SummaryType.weekly \
        else 'Daily'

    ReworkAndDefectsSummaryCompanyAdminManagerAdmin(). \
        set_subject('MBuild %s Summary - Rework & Defect Report: %s' % (summary_type, project.name,)). \
        set_to(to). \
        set_context(
        {
            **counters,
            'summary_type': summary_type,
            'project_name': project.name,
            'project_pk': project.pk,
            'today_date': pendulum.now()
        }). \
        send()


def send_summary_for_subcontractor(project: Project, summary_type: SummaryType, counters: dict):
    to = list(
        project.projectuser_set.filter(
            user__group=User.Group.SUBCONTRACTOR.value,
            is_notifications_enabled=True
        ).all().values_list('user__email', flat=True)
    )

    summary_type = 'Weekly' \
        if summary_type == SummaryType.weekly \
        else 'Daily'

    SummarySubcontractor(). \
        set_subject('MBuild %s Summary - Rework & Defect Report: %s' % (summary_type, project.name,)). \
        set_to(to). \
        set_context(
        {
            **counters,
            'summary_type': summary_type,
            'project_name': project.name,
            'project_pk': project.pk,
            'today_date': pendulum.now()
        }). \
        send()
