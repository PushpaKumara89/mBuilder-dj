from django_rq import job

from api.queues.core.summaries import send_summary_for_client as send_summary_for_client_core, \
    send_summary_for_consultant as send_summary_for_consultant_core, \
    send_task_summary_for_company_admin_manager_admin as send_task_summary_for_company_admin_manager_admin_core, \
    send_quality_issues_subtasks_summary_for_company_admin_manager_admin as send_quality_issues_subtasks_summary_for_company_admin_manager_admin_core, \
    send_summary_for_subcontractor as send_summary_for_subcontractor_core

from api.enums import SummaryType
from api.models import Project


@job('summaries', timeout=3600)
def send_summary_for_client(project: Project, summary_type: SummaryType, counters: dict):
    send_summary_for_client_core(project, summary_type, counters)


@job('summaries', timeout=3600)
def send_summary_for_consultant(project: Project, summary_type: SummaryType, company_pk: int, counters: dict):
    send_summary_for_consultant_core(project, summary_type, company_pk, counters)


@job('summaries', timeout=3600)
def send_task_summary_for_company_admin_manager_admin(project: Project, summary_type: SummaryType, counters: dict):
    send_task_summary_for_company_admin_manager_admin_core(project, summary_type, counters)


@job('summaries', timeout=3600)
def send_quality_issues_subtasks_summary_for_company_admin_manager_admin(project: Project, summary_type: SummaryType, counters: dict):
    send_quality_issues_subtasks_summary_for_company_admin_manager_admin_core(project, summary_type, counters)


@job('summaries', timeout=3600)
def send_summary_for_subcontractor(project: Project, summary_type: SummaryType, counters: dict):
    send_summary_for_subcontractor_core(project, summary_type, counters)
