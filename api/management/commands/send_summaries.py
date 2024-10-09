from datetime import timedelta

import pendulum
from django.core.management.base import BaseCommand
from django.db.models import Q, F, ExpressionWrapper, DateTimeField

from api.enums import SummaryType
from api.models import Project, QualityIssue, Task, TaskUpdate, Subtask, User
from api.queues.summaries import send_summary_for_client, send_summary_for_subcontractor, \
    send_task_summary_for_company_admin_manager_admin, \
    send_quality_issues_subtasks_summary_for_company_admin_manager_admin, send_summary_for_consultant


class Command(BaseCommand):
    help = "Send summaries"

    def add_arguments(self, parser):
        parser.add_argument('type', type=SummaryType, choices=list(SummaryType))

    def handle(self, *args, **options):
        summary_type = options['type']
        projects = Project.objects.exclude(status__in=[
            Project.Status.TENDERING,
            Project.Status.COMPLETED,
            Project.Status.ARCHIVED
        ]).all()

        for project in projects:
            self.send_for_client(summary_type, project)
            self.send_for_consultant(summary_type, project)
            self.send_for_company_admin_admin_manager(summary_type, project)
            self.send_for_subcontractor(summary_type, project)

    def send_for_client(self, summary_type: SummaryType, project: Project):
        creation_date = (
            pendulum.now().subtract(weeks=1)
            if summary_type == SummaryType.weekly
            else pendulum.now().subtract(days=1)
        )

        count_raised_under_review_quality_issues = QualityIssue.objects.filter(
            location_matrix__project=project,
            status=QualityIssue.Status.UNDER_REVIEW,
            created_at__gte=creation_date
        ).distinct().count()

        count_raised_in_urgent_attention_under_review_quality_issues = (
            QualityIssue.objects.annotate(due_date_range_end=ExpressionWrapper(F('created_at') + timedelta(hours=6),
                                                                               output_field=DateTimeField()))
            .filter(
                Q(Q(qualityissueupdate__old_data__status__isnull=True, qualityissueupdate__recipients__isnull=False) |
                  Q(qualityissueupdate__old_data__status__isnull=True, qualityissueupdate__recipients__isnull=True,
                    due_date__isnull=False, due_date__range=(F('created_at'), F('due_date_range_end')))),
                location_matrix__project=project,
                status=QualityIssue.Status.UNDER_REVIEW,
                created_at__gte=creation_date,
            ).distinct().count()
        )

        contested_count = QualityIssue.objects.filter(
            Q(qualityissueupdate__new_data__status=QualityIssue.Status.CONTESTED,
              qualityissueupdate__created_at__gte=creation_date),
            location_matrix__project=project,
            status=QualityIssue.Status.CONTESTED,
        ).distinct().count()

        closed_count = QualityIssue.objects.filter(
            Q(qualityissueupdate__created_at__gte=creation_date,
              qualityissueupdate__new_data__status=QualityIssue.Status.CLOSED),
            location_matrix__project=project,
            status=QualityIssue.Status.CLOSED
        ).distinct().count()

        removed_by_originator_count = QualityIssue.objects.filter(
            Q(qualityissueupdate__created_at__gte=creation_date,
              qualityissueupdate__new_data__status=QualityIssue.Status.REMOVED),
            location_matrix__project=project,
            qualityissueupdate__user=F('user'),
            status=QualityIssue.Status.REMOVED
        ).distinct().count()

        requesting_approval_count = QualityIssue.objects.filter(
            Q(qualityissueupdate__created_at__gte=creation_date,
              qualityissueupdate__new_data__status=QualityIssue.Status.REQUESTING_APPROVAL),
            location_matrix__project=project,
            status=QualityIssue.Status.REQUESTING_APPROVAL
        ).distinct().count()

        in_progress_count = QualityIssue.objects.filter(
            location_matrix__project=project,
            status=QualityIssue.Status.IN_PROGRESS,
        ).distinct().count()

        under_inspection_count = QualityIssue.objects.filter(
            Q(qualityissueupdate__created_at__gte=creation_date,
              qualityissueupdate__new_data__status=QualityIssue.Status.UNDER_INSPECTION),
            status=QualityIssue.Status.UNDER_INSPECTION,
            location_matrix__project=project,
        ).distinct().count()

        if any([closed_count, in_progress_count, requesting_approval_count, count_raised_under_review_quality_issues,
                count_raised_in_urgent_attention_under_review_quality_issues, contested_count, under_inspection_count,
                removed_by_originator_count]):
            send_summary_for_client(project, summary_type, {
                'contested_count': contested_count,
                'closed_count': closed_count,
                'in_progress_count': in_progress_count,
                'requesting_approval_count': requesting_approval_count,
                'count_raised_under_review_quality_issues': count_raised_under_review_quality_issues,
                'count_raised_in_urgent_attention_under_review_quality_issues': count_raised_in_urgent_attention_under_review_quality_issues,
                'removed_by_originator_count': removed_by_originator_count,
                'under_inspection_count': under_inspection_count,
            })

    def send_for_consultant(self, summary_type: SummaryType, project: Project):
        companies_pks = project.projectuser_set.filter(
            user__group=User.Group.CONSULTANT.value,
            is_notifications_enabled=True
        ).values_list('user__company', flat=True).distinct()

        for company_pk in companies_pks:
            creation_date = (
                pendulum.now().subtract(weeks=1)
                if summary_type == SummaryType.weekly
                else pendulum.now().subtract(days=1)
            )

            count_raised_under_review_quality_issues = QualityIssue.objects.filter(
                location_matrix__project=project,
                status=QualityIssue.Status.UNDER_REVIEW,
                created_at__gte=creation_date,
                user__company__pk=company_pk
            ).distinct().count()

            count_raised_in_urgent_attention_under_review_quality_issues = (
                QualityIssue.objects.annotate(
                    due_date_range_end=ExpressionWrapper(F('created_at') + timedelta(hours=6),
                                                         output_field=DateTimeField()))
                .filter(
                    Q(Q(qualityissueupdate__old_data__status__isnull=True,
                        qualityissueupdate__recipients__isnull=False) |
                      Q(qualityissueupdate__old_data__status__isnull=True, qualityissueupdate__recipients__isnull=True,
                        due_date__isnull=False, due_date__range=(F('created_at'), F('due_date_range_end')))),
                    location_matrix__project=project,
                    status=QualityIssue.Status.UNDER_REVIEW,
                    created_at__gte=creation_date,
                    user__company__pk=company_pk
                ).distinct().count()
            )

            contested_count = QualityIssue.objects.filter(
                Q(qualityissueupdate__new_data__status=QualityIssue.Status.CONTESTED,
                  qualityissueupdate__created_at__gte=creation_date),
                location_matrix__project=project,
                status=QualityIssue.Status.CONTESTED,
                user__company__pk=company_pk
            ).distinct().count()

            closed_count = QualityIssue.objects.filter(
                Q(qualityissueupdate__created_at__gte=creation_date,
                  qualityissueupdate__new_data__status=QualityIssue.Status.CLOSED),
                location_matrix__project=project,
                status=QualityIssue.Status.CLOSED,
                user__company__pk=company_pk
            ).distinct().count()

            removed_by_originator_count = QualityIssue.objects.filter(
                Q(qualityissueupdate__created_at__gte=creation_date,
                  qualityissueupdate__new_data__status=QualityIssue.Status.REMOVED),
                location_matrix__project=project,
                qualityissueupdate__user=F('user'),
                status=QualityIssue.Status.REMOVED,
                user__company__pk=company_pk
            ).distinct().count()

            requesting_approval_count = QualityIssue.objects.filter(
                Q(qualityissueupdate__created_at__gte=creation_date,
                  qualityissueupdate__new_data__status=QualityIssue.Status.REQUESTING_APPROVAL),
                location_matrix__project=project,
                status=QualityIssue.Status.REQUESTING_APPROVAL,
                user__company__pk=company_pk
            ).distinct().count()

            in_progress_count = QualityIssue.objects.filter(
                location_matrix__project=project,
                status=QualityIssue.Status.IN_PROGRESS,
                user__company__pk=company_pk
            ).distinct().count()

            under_inspection_count = QualityIssue.objects.filter(
                Q(qualityissueupdate__created_at__gte=creation_date,
                  qualityissueupdate__new_data__status=QualityIssue.Status.UNDER_INSPECTION),
                status=QualityIssue.Status.UNDER_INSPECTION,
                location_matrix__project=project,
                user__company__pk=company_pk
            ).distinct().count()

            if any([closed_count, in_progress_count, requesting_approval_count, contested_count, under_inspection_count,
                    count_raised_in_urgent_attention_under_review_quality_issues, removed_by_originator_count,
                    count_raised_under_review_quality_issues]):
                send_summary_for_consultant(project, summary_type, company_pk, {
                    'contested_count': contested_count,
                    'closed_count': closed_count,
                    'in_progress_count': in_progress_count,
                    'requesting_approval_count': requesting_approval_count,
                    'count_raised_under_review_quality_issues': count_raised_under_review_quality_issues,
                    'count_raised_in_urgent_attention_under_review_quality_issues': count_raised_in_urgent_attention_under_review_quality_issues,
                    'removed_by_originator_count': removed_by_originator_count,
                    'under_inspection_count': under_inspection_count,
                })

    def send_for_company_admin_admin_manager(self, summary_type: SummaryType, project: Project):
        creation_date = (
            pendulum.now().subtract(weeks=1)
            if summary_type == SummaryType.weekly
            else pendulum.now().subtract(days=1)
        )

        accepted_tasks_count = TaskUpdate.objects.filter(
            task__location_matrix__project=project,
            created_at__gte=creation_date,
            new_data__status=Task.Statuses.ACCEPTED,
            task__status=Task.Statuses.ACCEPTED
        ).count()

        partially_completed_tasks_count = TaskUpdate.objects.filter(
            task__location_matrix__project=project,
            created_at__gte=creation_date,
            new_data__status=Task.Statuses.PART_COMPLETE,
            task__status=Task.Statuses.PART_COMPLETE
        ).count()

        not_verified_tasks_count = TaskUpdate.objects.filter(
            task__location_matrix__project=project,
            created_at__gte=creation_date,
            new_data__status=Task.Statuses.NOT_VERIFIED,
            task__status=Task.Statuses.NOT_VERIFIED
        ).count()

        rejected_tasks_count = TaskUpdate.objects.filter(
            task__location_matrix__project=project,
            created_at__gte=creation_date,
            new_data__status=Task.Statuses.REJECTED,
            task__status=Task.Statuses.REJECTED
        ).count()

        if any([accepted_tasks_count, partially_completed_tasks_count, not_verified_tasks_count, rejected_tasks_count]):
            send_task_summary_for_company_admin_manager_admin(project, summary_type, {
                'accepted_tasks_count': accepted_tasks_count,
                'partially_completed_tasks_count': partially_completed_tasks_count,
                'not_verified_tasks_count': not_verified_tasks_count,
                'rejected_tasks_count': rejected_tasks_count,
            })

        under_review_qi_count = QualityIssue.objects.filter(
            location_matrix__project=project,
            status=QualityIssue.Status.UNDER_REVIEW,
            created_at__gte=creation_date
        ).distinct().count()

        raised_required_attention_qi_count = (
            QualityIssue.objects.annotate(
                due_date_range_end=ExpressionWrapper(F('created_at') + timedelta(hours=6),
                                                     output_field=DateTimeField()))
            .filter(
                Q(Q(qualityissueupdate__old_data__status__isnull=True, qualityissueupdate__recipients__isnull=False) |
                  Q(qualityissueupdate__old_data__status__isnull=True, qualityissueupdate__recipients__isnull=True,
                    due_date__isnull=False, due_date__range=(F('created_at'), F('due_date_range_end')))),
                location_matrix__project=project,
                status=QualityIssue.Status.UNDER_REVIEW,
                created_at__gte=creation_date,
            ).distinct().count()
        )

        contested_qi_count = QualityIssue.objects.filter(
            Q(qualityissueupdate__created_at__gte=creation_date,
              qualityissueupdate__new_data__status=QualityIssue.Status.CONTESTED),
            location_matrix__project=project,
        ).distinct().count()

        new_subtasks_count = Subtask.objects.filter(
            user__group__in=[User.Group.COMPANY_ADMIN.value, User.Group.ADMIN.value, User.Group.MANAGER.value],
            task__location_matrix__project=project,
            created_at__gte=creation_date,
            company__isnull=False,
            status=Subtask.Status.IN_PROGRESS
        ).distinct().count()

        closed_subtasks_count = Subtask.objects.filter(
            Q(subtaskupdate__new_data__status=Subtask.Status.CLOSED,
              subtaskupdate__created_at__gte=creation_date),
            task__location_matrix__project=project
        ).distinct().count()

        requested_approval_subtasks_count = Subtask.objects.filter(
            Q(subtaskupdate__new_data__status=Subtask.Status.REQUESTING_APPROVAL,
              subtaskupdate__created_at__gte=creation_date),
            task__location_matrix__project=project,
            status=Subtask.Status.REQUESTING_APPROVAL
        ).distinct().count()

        in_progress_subtasks_count = Subtask.objects.filter(
            task__location_matrix__project=project,
            status=Subtask.Status.IN_PROGRESS
        ).distinct().count()

        under_inspection_subtasks_count = Subtask.objects.filter(
            Q(subtaskupdate__new_data__status=Subtask.Status.UNDER_INSPECTION,
              subtaskupdate__created_at__gte=creation_date),
            task__location_matrix__project=project,
            status=Subtask.Status.UNDER_INSPECTION
        ).distinct().count()

        overdue_subtasks_count = Subtask.objects.filter(
            status__in=[
                Subtask.Status.IN_PROGRESS,
                Subtask.Status.DECLINED,
                Subtask.Status.UNDER_INSPECTION,
                Subtask.Status.INSPECTION_REJECTED,
                Subtask.Status.REQUESTING_APPROVAL,
                Subtask.Status.REQUESTED_APPROVAL_REJECTED
            ],
            task__location_matrix__project=project,
            due_date__lt=pendulum.now().to_datetime_string()
        ).distinct().count()

        if any([under_review_qi_count, raised_required_attention_qi_count, contested_qi_count, new_subtasks_count,
                closed_subtasks_count, requested_approval_subtasks_count, in_progress_subtasks_count,
                under_inspection_subtasks_count, overdue_subtasks_count]):
            send_quality_issues_subtasks_summary_for_company_admin_manager_admin(project, summary_type, {
                'under_review_qi_count': under_review_qi_count,
                'raised_required_attention_qi_count': raised_required_attention_qi_count,
                'contested_qi_count': contested_qi_count,
                'new_subtasks_count': new_subtasks_count,
                'closed_subtasks_count': closed_subtasks_count,
                'requested_approval_subtasks_count': requested_approval_subtasks_count,
                'in_progress_subtasks_count': in_progress_subtasks_count,
                'under_inspection_subtasks_count': under_inspection_subtasks_count,
                'overdue_subtasks_count': overdue_subtasks_count,
            })

    def send_for_subcontractor(self, summary_type: SummaryType, project: Project):
        creation_date = (
            pendulum.now().subtract(weeks=1)
            if summary_type == SummaryType.weekly
            else pendulum.now().subtract(days=1)
        )

        in_progress_count = Subtask.objects.filter(
            task__location_matrix__project=project,
            status=Subtask.Status.IN_PROGRESS,
            created_at__gte=creation_date
        ).distinct().count()

        raised_required_attention_count = (
            Subtask.objects.annotate(
                due_date_range_end=ExpressionWrapper(F('created_at') + timedelta(hours=6),
                                                     output_field=DateTimeField()))
            .filter(
                Q(Q(subtaskupdate__old_data__status__isnull=True, subtaskupdate__recipients__isnull=False) |
                  Q(subtaskupdate__old_data__status__isnull=True, subtaskupdate__recipients__isnull=True,
                    due_date__isnull=False, due_date__range=(F('created_at'), F('due_date_range_end')))),
                task__location_matrix__project=project,
                status=Subtask.Status.IN_PROGRESS,
                created_at__gte=creation_date,
            ).distinct().count()
        )

        declined_count = Subtask.objects.filter(
            Q(subtaskupdate__created_at__gte=creation_date,
              subtaskupdate__new_data__status=Subtask.Status.DECLINED),
            task__location_matrix__project=project,
            status=Subtask.Status.DECLINED
        ).distinct().count()

        under_inspection_count = Subtask.objects.filter(
            Q(subtaskupdate__created_at__gte=creation_date,
              subtaskupdate__new_data__status=Subtask.Status.UNDER_INSPECTION),
            task__location_matrix__project=project,
            status=Subtask.Status.UNDER_INSPECTION
        ).distinct().count()

        closed_count = Subtask.objects.filter(
            Q(subtaskupdate__created_at__gte=creation_date,
              subtaskupdate__new_data__status=Subtask.Status.CLOSED),
            task__location_matrix__project=project,
        ).distinct().count()

        requesting_approval_count = Subtask.objects.filter(
            Q(subtaskupdate__created_at__gte=creation_date,
              subtaskupdate__new_data__status=Subtask.Status.REQUESTING_APPROVAL),
            task__location_matrix__project=project,
            quality_issue__isnull=False,
            status=Subtask.Status.REQUESTING_APPROVAL
        ).distinct().count()

        all_in_progress_count = Subtask.objects.filter(
            task__location_matrix__project=project,
            status=Subtask.Status.IN_PROGRESS
        ).distinct().count()

        overdue_count = Subtask.objects.filter(
            task__location_matrix__project=project,
            due_date__lt=pendulum.now().to_datetime_string()
        ).distinct().count()

        if any([in_progress_count, raised_required_attention_count, declined_count, under_inspection_count,
                closed_count, requesting_approval_count, all_in_progress_count, overdue_count]):
            send_summary_for_subcontractor(project, summary_type, {
                'in_progress_count': in_progress_count,
                'raised_required_attention_count': raised_required_attention_count,
                'declined_count': declined_count,
                'under_inspection_count': under_inspection_count,
                'closed_count': closed_count,
                'requesting_approval_count': requesting_approval_count,
                'all_in_progress_count': all_in_progress_count,
                'overdue_count': overdue_count,
            })
