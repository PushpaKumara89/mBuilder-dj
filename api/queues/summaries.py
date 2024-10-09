from api.queues.core.base import use_rq_if_configured

from api.queues.rq.summaries import send_summary_for_client as send_summary_for_client_rq, \
    send_summary_for_consultant as send_summary_for_consultant_rq, \
    send_task_summary_for_company_admin_manager_admin as send_task_summary_for_company_admin_manager_admin_rq, \
    send_quality_issues_subtasks_summary_for_company_admin_manager_admin as send_quality_issues_subtasks_summary_for_company_admin_manager_admin_rq, \
    send_summary_for_subcontractor as send_summary_for_subcontractor_rq

from api.queues.celery.summaries import send_summary_for_client as send_summary_for_client_celery, \
    send_summary_for_consultant as send_summary_for_consultant_celery, \
    send_task_summary_for_company_admin_manager_admin as send_task_summary_for_company_admin_manager_admin_celery, \
    send_quality_issues_subtasks_summary_for_company_admin_manager_admin as send_quality_issues_subtasks_summary_for_company_admin_manager_admin_celery, \
    send_summary_for_subcontractor as send_summary_for_subcontractor_celery

from api.enums import SummaryType
from api.models import Project


@use_rq_if_configured(send_summary_for_client_rq)
def send_summary_for_client(project: Project, summary_type: SummaryType, counters: dict):
    send_summary_for_client_celery.delay(project, summary_type, counters)


@use_rq_if_configured(send_summary_for_consultant_rq)
def send_summary_for_consultant(project: Project, summary_type: SummaryType, company_pk: int, counters: dict):
    send_summary_for_consultant_celery.delay(project, summary_type, company_pk, counters)


@use_rq_if_configured(send_task_summary_for_company_admin_manager_admin_rq)
def send_task_summary_for_company_admin_manager_admin(project: Project, summary_type: SummaryType, counters: dict):
    send_task_summary_for_company_admin_manager_admin_celery.delay(project, summary_type, counters)


@use_rq_if_configured(send_quality_issues_subtasks_summary_for_company_admin_manager_admin_rq)
def send_quality_issues_subtasks_summary_for_company_admin_manager_admin(project: Project, summary_type: SummaryType, counters: dict):
    send_quality_issues_subtasks_summary_for_company_admin_manager_admin_celery.delay(project, summary_type, counters)


@use_rq_if_configured(send_summary_for_subcontractor_rq)
def send_summary_for_subcontractor(project: Project, summary_type: SummaryType, counters: dict):
    send_summary_for_subcontractor_celery.delay(project, summary_type, counters)
