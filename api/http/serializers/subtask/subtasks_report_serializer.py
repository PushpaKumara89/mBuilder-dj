from enum import Enum

import pendulum
from django.conf import settings
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import fields, serializers

from api.http.serializers import MediaSerializer
from api.models import Task, Subtask, User, QualityIssue
from api.utilities.report_utilities import ReportUtilities
from api.utilities.time_utilities import change_timezone_to_london


class SubtasksReportSerializer(FlexFieldsModelSerializer):
    class ExportProducer(Enum):
        CSV = 1
        PDF = 2

    class Meta:
        model = Subtask
        fields = (
            'id', 'description', 'is_closed', 'task', 'user', 'files', 'created_at',
            'updated_at', 'quality_issue', 'location_description', 'status', 'is_defect',
            'subcontractor_company', 'subcontractor_name',
        )
        expandable_fields = {
            'expanded_date_of_completion': (serializers.SerializerMethodField, {'method_name': 'date_of_completion'}),
            'expanded_time_of_completion': (serializers.SerializerMethodField, {'method_name': 'time_of_completion'}),
            'expanded_action_required_by': (serializers.SerializerMethodField, {'method_name': 'action_required_by'}),
            'expanded_project_name': (serializers.SerializerMethodField, {'method_name': 'project_name'}),
            'expanded_project_number': (serializers.SerializerMethodField, {'method_name': 'project_number'}),
            'expanded_status_name': (serializers.SerializerMethodField, {'method_name': 'status_name'}),
            'expanded_package': (serializers.SerializerMethodField, {'method_name': 'package'}),
            'expanded_package_activity_name': (serializers.SerializerMethodField, {'method_name': 'package_activity_name'}),
            'expanded_package_activity_id': (serializers.SerializerMethodField, {'method_name': 'package_activity_id'}),
            'expanded_package_activity_task_description': (serializers.SerializerMethodField, {'method_name': 'package_activity_task_description'}),
            'expanded_building': (serializers.SerializerMethodField, {'method_name': 'building'}),
            'expanded_level': (serializers.SerializerMethodField, {'method_name': 'level'}),
            'expanded_area': (serializers.SerializerMethodField, {'method_name': 'area'}),
            'expanded_files_urls': (serializers.SerializerMethodField, {'method_name': 'files_urls'}),
            'expanded_files_urls_array': (serializers.SerializerMethodField, {'method_name': 'files_urls_array'}),
            'expanded_date_raised': (serializers.SerializerMethodField, {'method_name': 'date_raised'}),
            'expanded_time_raised': (serializers.SerializerMethodField, {'method_name': 'time_raised'}),
            'expanded_identified_user': (serializers.SerializerMethodField, {'method_name': 'identified_user'}),
            'expanded_identified_user_company': (serializers.SerializerMethodField, {'method_name': 'identified_user_company'}),
            'expanded_recipients': (serializers.SerializerMethodField, {'method_name': 'recipients'}),
            'expanded_due_date': (serializers.SerializerMethodField, {'method_name': 'due_date'}),
            'expanded_due_time': (serializers.SerializerMethodField, {'method_name': 'due_time'}),
            'expanded_estimation': (serializers.SerializerMethodField, {'method_name': 'estimation'}),
            'expanded_user_closed': (serializers.SerializerMethodField, {'method_name': 'user_closed'}),
            'expanded_user_closed_company': (serializers.SerializerMethodField, {'method_name': 'user_closed_company'}),
            'expanded_closed_comments': (serializers.SerializerMethodField, {'method_name': 'closed_comments'}),
            'expanded_closed_files_urls': (serializers.SerializerMethodField, {'method_name': 'closed_files_urls'}),
            'expanded_closed_files_urls_array': (serializers.SerializerMethodField, {'method_name': 'closed_files_urls_array'}),
            'expanded_last_status': (serializers.SerializerMethodField, {'method_name': 'last_status'}),
            'expanded_last_user': (serializers.SerializerMethodField, {'method_name': 'last_user'}),
            'expanded_last_update_date': (serializers.SerializerMethodField, {'method_name': 'last_update_date'}),
            'expanded_last_update_time': (serializers.SerializerMethodField, {'method_name': 'last_update_time'}),
            'expanded_is_overdue': (serializers.SerializerMethodField, {'method_name': 'is_overdue'}),
            'expanded_last_comment': (serializers.SerializerMethodField, {'method_name': 'last_comment'}),
        }

    description = fields.CharField(required=True)
    status = fields.CharField(read_only=True)
    location_description = fields.CharField(required=False, allow_null=True, max_length=50)
    is_closed = fields.BooleanField(read_only=True)
    is_defect = fields.BooleanField(read_only=True)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    files = MediaSerializer(source='files_set', many=True, required=False, read_only=True)
    quality_issue = serializers.PrimaryKeyRelatedField(queryset=QualityIssue.objects.all())

    created_at = fields.DateTimeField(read_only=True, format=settings.DATE_FORMAT)
    updated_at = fields.DateTimeField(read_only=True, format=settings.DATE_FORMAT)

    subcontractor_company = serializers.SerializerMethodField()
    subcontractor_name = serializers.SerializerMethodField()

    def __init__(self, *args, export_producer: ExportProducer = ExportProducer.PDF, **kwargs):
        self.export_producer = export_producer

        super().__init__(*args, **kwargs)

    def last_comment(self, obj: Subtask) -> str | None:
        comment_update = obj.subtaskupdate_set.filter(is_comment=True).order_by('-created_at').first()
        return comment_update.comment if comment_update else None

    def get_subcontractor_company(self, obj) -> str:
        if getattr(obj, 'company', False):
            return obj.company.name
        return ''

    def get_subcontractor_name(self, obj) -> str:
        if getattr(obj.task, 'project', False):
            filters = {'group_id': User.Group.SUBCONTRACTOR}
            if getattr(obj, 'company', False):
                filters['company_id'] = obj.company_id
            return '\n'.join([user.get_full_name() for user in obj.task.project.users.filter(**filters)])
        return ''

    def _format_date(self, date):
        if not date:
            return ''
        date_tz = change_timezone_to_london(date)
        if self.export_producer == self.ExportProducer.PDF:
            return f"{date_tz.strftime('%d %b, %Y')}\n{date_tz.strftime('%I:%M%p')}"

        return date_tz.strftime('%d/%m/%Y')

    def _format_time(self, date):
        if not date:
            return ''
        date_tz = change_timezone_to_london(date)
        return date_tz.strftime('%I:%M %p')

    def date_of_completion(self, obj: Subtask):
        return self._format_date(obj.date_of_completion)

    def time_of_completion(self, obj: Subtask):
        return self._format_time(obj.date_of_completion)

    def status_name(self, obj: Subtask):
        return obj.get_to_report_status_name()

    def project_number(self, obj: Subtask):
        return obj.task.location_matrix.project.number

    def action_required_by(self, obj: Subtask):
        if obj.status == Subtask.Status.IN_PROGRESS.value and obj.company is None:
            return 'Multiplex'
        elif obj.status == Subtask.Status.IN_PROGRESS.value and obj.company is not None:
            return obj.company.name
        elif obj.status == Subtask.Status.UNDER_INSPECTION.value:
            return 'Multiplex'
        elif obj.status == Subtask.Status.DECLINED.value:
            return 'Multiplex'
        elif obj.status == Subtask.Status.CONTESTED.value:
            return obj.quality_issue.user.company.name if obj.quality_issue else obj.company.name
        elif obj.status == Subtask.Status.INSPECTION_REJECTED.value and obj.company is None:
            return 'Multiplex'
        elif obj.status == Subtask.Status.INSPECTION_REJECTED.value and obj.company is not None:
            return obj.company.name
        elif obj.status == Subtask.Status.REQUESTING_APPROVAL.value:
            return obj.quality_issue.user.company.name if obj.quality_issue else obj.company.name
        elif obj.status == Subtask.Status.REQUESTED_APPROVAL_REJECTED.value:
            return 'Multiplex'

        return ''

    def project_name(self, obj: Subtask):
        return obj.task.location_matrix.project.name

    def package(self, obj: Subtask):
        package_matrices = (obj.task.location_matrix.project.packagematrix_set
                            .filter(package_activity=obj.task.package_activity)
                            .select_related('package')
                            .all(force_visibility=True))

        package_matrix = package_matrices.filter(deleted__isnull=True).first() or package_matrices.first()

        return package_matrix.package.name if package_matrix else None

    def package_activity_name(self, obj: Subtask):
        return obj.task.package_activity.name

    def package_activity_id(self, obj: Subtask):
        return obj.task.package_activity.activity_id or ''

    def package_activity_task_description(self, obj: Subtask):
        return obj.task.package_activity_task.description

    def building(self, obj: Subtask):
        return obj.task.location_matrix.building

    def level(self, obj: Subtask):
        return obj.task.location_matrix.level

    def area(self, obj: Subtask):
        return obj.task.location_matrix.area

    def files_urls(self, obj: Subtask):
        files_urls = [ReportUtilities.get_file_link(file) for file in obj.files.all()]

        return ' '.join(files_urls)

    def files_urls_array(self, obj: Subtask) -> dict:
        obj_files = obj.files.all()
        return ReportUtilities().get_files_and_images(obj_files)

    def closed_files_urls_array(self, obj: Subtask):
        closing_update = (obj.subtaskupdate_set
                          .prefetch_related('files')
                          .filter(new_data__status=Subtask.Status.CLOSED)
                          .prefetch_related('files')
                          .order_by('-created_at')
                          .first())
        if closing_update:
            update_files = closing_update.files.all()
            return ReportUtilities().get_files_and_images(update_files)

        return {}

    def identified_user(self, obj: Subtask):
        return obj.user.get_full_name()

    def identified_user_company(self, obj: Subtask):
        return obj.user.company.name

    def date_raised(self, obj: Subtask):
        return self._format_date(obj.created_at)

    def time_raised(self, obj: Subtask):
        return self._format_time(obj.created_at)

    def recipients(self, obj: Subtask):
        update_history = obj.subtaskupdate_set.all().prefetch_related('recipients').order_by('created_at')
        result = ''

        for count, update in enumerate(update_history, start=1):
            recipients = [recipient.email for recipient in update.recipients.all()]
            result += f"{count} {', '.join(recipients)}\n"

        return result

    def due_date(self, obj: Subtask):
        return self._format_date(obj.due_date)

    def due_time(self, obj: Subtask):
        return self._format_time(obj.due_date)

    def estimation(self, obj: Subtask):
        return obj.estimation

    def user_closed(self, obj: Subtask):
        closing_update = (obj.subtaskupdate_set
                          .filter(new_data__status=Subtask.Status.CLOSED)
                          .select_related('user')
                          .order_by('-created_at')
                          .first())

        return closing_update.user.get_full_name() if closing_update else ''

    def user_closed_company(self, obj: Subtask):
        closing_update = (obj.subtaskupdate_set
                          .filter(new_data__status=Subtask.Status.CLOSED)
                          .select_related('user__company')
                          .order_by('-created_at')
                          .first())

        return closing_update.user.company.name if closing_update else ''

    def closed_comments(self, obj: Subtask):
        closing_update = (obj.subtaskupdate_set
                          .filter(new_data__status=Subtask.Status.CLOSED)
                          .order_by('-created_at')
                          .first())

        return closing_update.comment if closing_update else ''

    def closed_files_urls(self, obj: Subtask):
        return ', '.join(self._get_closed_files_urls(obj))

    def last_status(self, obj: Subtask):
        return obj.get_to_report_status_name()

    def last_user(self, obj: Subtask):
        update = obj.subtaskupdate_set.order_by('-created_at').select_related('user').first()
        if update:
            return update.user.get_full_name()
        return ''

    def last_update_date(self, obj: Subtask):
        update = obj.subtaskupdate_set.order_by('-created_at').first()
        return self._format_date(getattr(update, 'created_at', None))

    def last_update_time(self, obj: Subtask):
        update = obj.subtaskupdate_set.order_by('-created_at').first()
        return self._format_time(getattr(update, 'created_at', None))

    def is_overdue(self, obj: Subtask):
        return (obj.status not in [Subtask.Status.CLOSED,
                                   Subtask.Status.REMOVED,
                                   Subtask.Status.UNDER_INSPECTION,
                                   Subtask.Status.REQUESTING_APPROVAL]
                and obj.due_date < pendulum.now())

    def _get_closed_files_urls(self, obj: Subtask):
        closing_update = (obj.subtaskupdate_set
                          .prefetch_related('files')
                          .filter(new_data__status=Subtask.Status.CLOSED)
                          .prefetch_related('files')
                          .order_by('-created_at')
                          .first())

        if closing_update:
            return [ReportUtilities.get_file_link(media) for media in closing_update.files.all()]

        return []
