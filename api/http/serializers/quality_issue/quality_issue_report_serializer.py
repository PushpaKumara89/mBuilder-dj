from datetime import datetime
from enum import Enum
from typing import Optional

import pendulum

from rest_framework import serializers

from api.http.serializers import RecipientSerializer, QualityIssueUpdateSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import QualityIssue, LocationMatrix, Media, User, ResponseCategory, QualityIssueUpdate
from api.utilities.report_utilities import ReportUtilities
from api.utilities.time_utilities import change_timezone_to_london


class QualityIssueReportSerializer(BaseModelSerializer):
    class ExportProducer(Enum):
        CSV = 1
        PDF = 2

    class Meta:
        model = QualityIssue
        fields = ('id', 'location_matrix', 'user', 'description', 'status', 'attachments',
                  'recipients', 'created_at', 'updated_at', 'due_date', 'last_confirmed_update',
                  'old_quality_issue', 'response_category',)
        expandable_fields = {
            'expanded_project_name': (serializers.SerializerMethodField, {'method_name': 'project_name'}),
            'expanded_project_number': (serializers.SerializerMethodField, {'method_name': 'project_number'}),
            'expanded_status_name': (serializers.SerializerMethodField, {'method_name': 'status_name'}),
            'expanded_action_required_by': (serializers.SerializerMethodField, {'method_name': 'action_required_by'}),
            'expanded_building': (serializers.SerializerMethodField, {'method_name': 'building'}),
            'expanded_level': (serializers.SerializerMethodField, {'method_name': 'level'}),
            'expanded_area': (serializers.SerializerMethodField, {'method_name': 'area'}),
            'expanded_package': (serializers.SerializerMethodField, {'method_name': 'package'}),
            'expanded_package_activity_name': (
                serializers.SerializerMethodField, {'method_name': 'package_activity_name'}),
            'expanded_package_activity_id': (serializers.SerializerMethodField, {'method_name': 'package_activity_id'}),
            'expanded_package_activity_task_description': (
                serializers.SerializerMethodField, {'method_name': 'package_activity_task_description'}),
            'expanded_created_by': (serializers.SerializerMethodField, {'method_name': 'created_by'}),
            'expanded_created_by_company_name': (
                serializers.SerializerMethodField, {'method_name': 'created_by_company_name'}),
            'expanded_due_date': (serializers.SerializerMethodField, {'method_name': 'expanded_due_date'}),
            'expanded_created_date': (serializers.SerializerMethodField, {'method_name': 'created_date'}),
            'expanded_created_time': (serializers.SerializerMethodField, {'method_name': 'created_time'}),
            'expanded_files_urls': (serializers.SerializerMethodField, {'method_name': 'files_urls'}),
            'expanded_files_urls_array': (serializers.SerializerMethodField, {'method_name': 'files_urls_array'}),
            'expanded_id': (serializers.SerializerMethodField, {'method_name': 'quality_issue_id'}),
            'expanded_status_by': (serializers.SerializerMethodField, {'method_name': 'status_by'}),
            'expanded_response_category': (
                serializers.SerializerMethodField, {'method_name': 'expanded_response_category'}),
            'expanded_is_overdue': (serializers.SerializerMethodField, {'method_name': 'is_overdue'}),
            'expanded_user_closed': (serializers.SerializerMethodField, {'method_name': 'user_closed'}),
            'expanded_user_closed_company': (serializers.SerializerMethodField, {'method_name': 'user_closed_company'}),
            'expanded_closed_comments': (serializers.SerializerMethodField, {'method_name': 'closed_comments'}),
            'expanded_closed_files_urls_array': (
                serializers.SerializerMethodField, {'method_name': 'closed_files_urls_array'}),
            'expanded_date_of_completion': (serializers.SerializerMethodField, {'method_name': 'date_of_completion'}),
            'expanded_response_date': (serializers.SerializerMethodField, {'method_name': 'response_date'}),
            'expanded_response_time': (serializers.SerializerMethodField, {'method_name': 'response_time'}),
            'expanded_latest_comment': (serializers.SerializerMethodField, {'method_name': 'latest_comment'}),
            'expanded_latest_comment_user': (serializers.SerializerMethodField, {'method_name': 'latest_comment_user'}),
            'expanded_latest_comment_date': (serializers.SerializerMethodField, {'method_name': 'latest_comment_date'}),
        }

    location_matrix = serializers.PrimaryKeyRelatedField(queryset=LocationMatrix.objects.all(), required=True)
    description = serializers.CharField(required=True)
    status = serializers.ChoiceField(choices=QualityIssue.Status.choices, read_only=True)
    attachments = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=False, many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    recipients = RecipientSerializer(required=False, many=True)
    due_date = serializers.DateTimeField(required=True)
    last_confirmed_update = serializers.PrimaryKeyRelatedField(read_only=True)
    old_quality_issue = serializers.PrimaryKeyRelatedField(queryset=QualityIssue.objects.all(), required=False,
                                                           allow_null=True)
    response_category = serializers.PrimaryKeyRelatedField(queryset=ResponseCategory.objects.all(), default=None,
                                                           allow_null=True, required=False)

    def __init__(self, *args, export_producer: ExportProducer = ExportProducer.PDF, **kwargs):
        self.export_producer = export_producer

        super().__init__(*args, **kwargs)

    def latest_comment(self, obj: QualityIssue) -> str | None:
        comment_update = self._get_latest_comment(obj)
        return comment_update.comment if comment_update else None

    def latest_comment_user(self, obj: QualityIssue) -> str | None:
        comment_update = self._get_latest_comment(obj)
        return comment_update.user.get_full_name() if comment_update else None

    def latest_comment_date(self, obj: QualityIssue) -> str | None:
        comment_update = self._get_latest_comment(obj)
        return comment_update.created_at.strftime('%d %b, %Y') + '\n' + comment_update.created_at.strftime('%I:%M%p') \
            if comment_update \
            else None

    def project_name(self, obj: QualityIssue) -> str:
        return obj.location_matrix.project.name

    def project_number(self, obj: QualityIssue) -> str:
        return obj.location_matrix.project.number

    def status_name(self, obj: QualityIssue) -> str:
        if obj.is_inspection_rejected:
            return QualityIssue.Status.IN_PROGRESS.label
        return obj.get_to_report_status_name()

    def action_required_by(self, obj: QualityIssue) -> str:
        company = None
        if obj.subtask_set.count() > 0:
            company = obj.subtask_set.select_related('company').first().company

        if obj.status == QualityIssue.Status.IN_PROGRESS and company is None:
            return 'Multiplex'
        elif obj.status == QualityIssue.Status.IN_PROGRESS and company is not None:
            return company.name
        elif obj.status == QualityIssue.Status.UNDER_INSPECTION:
            return 'Multiplex'
        elif obj.status == QualityIssue.Status.DECLINED:
            return 'Multiplex'
        elif obj.status == QualityIssue.Status.CONTESTED:
            return obj.user.company.name
        elif obj.status == QualityIssue.Status.INSPECTION_REJECTED and company is None:
            return 'Multiplex'
        elif obj.status == QualityIssue.Status.INSPECTION_REJECTED and company is not None:
            return company.name
        elif obj.status == QualityIssue.Status.REQUESTING_APPROVAL:
            return obj.user.company.name
        elif obj.status == QualityIssue.Status.REQUESTED_APPROVAL_REJECTED:
            return 'Multiplex'

        return ''

    def package(self, obj: QualityIssue) -> str:
        package_name = None
        if obj.subtask_set.count() > 0:
            package_matrix = obj.location_matrix.project.packagematrix_set.filter(
                package_activity=obj.subtask_set.first().task.package_activity
            ).all(force_visibility=True).select_related('package').first()

            if package_matrix:
                package_name = package_matrix.package.name

        return package_name

    def package_activity_name(self, obj: QualityIssue) -> str:
        package_activity_name = ''
        if obj.subtask_set.count() > 0:
            package_activity_name = obj.subtask_set.select_related(
                'task__package_activity').first().task.package_activity.name

        return package_activity_name

    def package_activity_id(self, obj: QualityIssue) -> str:
        package_activity_id = ''
        if obj.subtask_set.count() > 0:
            package_activity_id = (obj.subtask_set.select_related('task__package_activity')
                                   .first().task.package_activity.activity_id)

        return package_activity_id

    def package_activity_task_description(self, obj: QualityIssue) -> str:
        package_activity_description = ''
        if obj.subtask_set.count() > 0:
            package_activity_description = (obj.subtask_set.select_related('task__package_activity_task')
                                            .first().task.package_activity_task.description)

        return package_activity_description

    def building(self, obj: QualityIssue) -> str:
        return obj.location_matrix.building

    def level(self, obj: QualityIssue) -> str:
        return obj.location_matrix.level

    def area(self, obj: QualityIssue) -> str:
        return obj.location_matrix.area

    def files_urls(self, obj: QualityIssue) -> str:
        generated_files_urls = [ReportUtilities.get_file_link(file) for file in obj.attachments.all()[:6]]

        return ', '.join(generated_files_urls)

    def files_urls_array(self, obj: QualityIssue) -> dict:
        obj_attachments = obj.attachments.all()[:6]
        return ReportUtilities.get_files_and_images(obj_attachments)

    def closed_files_urls_array(self, obj: QualityIssue) -> dict:
        if obj.status == QualityIssue.Status.CLOSED.value:
            closing_update = (
                obj.qualityissueupdate_set
                    .prefetch_related('files')
                    .filter(new_data__status=QualityIssue.Status.REQUESTING_APPROVAL)
                    .order_by('-created_at')
                    .first()
            )

            if closing_update:
                closing_files = closing_update.files.all()[:6]
                return ReportUtilities().get_files_and_images(closing_files)

        return {}

    def created_by(self, obj: QualityIssue) -> str:
        return obj.user.get_full_name()

    def created_by_company_name(self, obj: QualityIssue) -> str:
        return obj.user.company.name

    def expanded_due_date(self, obj: QualityIssue) -> str:
        if obj.due_date is None:
            return ''

        due_date = change_timezone_to_london(obj.created_at)

        return due_date.strftime('%d %b, %Y') + '\n' + due_date.strftime('%I:%M%p')

    def is_overdue(self, obj: QualityIssue) -> bool:
        return obj.status == QualityIssue.Status.UNDER_REVIEW and obj.due_date is not None and obj.due_date < pendulum.now()

    def user_closed(self, obj: QualityIssue) -> Optional[str]:
        user = None
        if obj.status == QualityIssue.Status.CLOSED.value:
            closing_update = obj.qualityissueupdate_set. \
                filter(new_data__status=QualityIssue.Status.CLOSED). \
                order_by('-created_at'). \
                first()

            user = closing_update.user.get_full_name() if closing_update else ''

        return user

    def user_closed_company(self, obj: QualityIssue) -> Optional[str]:
        company_name = None
        if obj.status == QualityIssue.Status.CLOSED.value:
            closing_update = obj.qualityissueupdate_set. \
                filter(new_data__status=QualityIssue.Status.CLOSED). \
                select_related('user__company'). \
                order_by('-created_at'). \
                first()

            company_name = closing_update.user.company.name if closing_update else ''

        return company_name

    def closed_comments(self, obj: QualityIssue) -> Optional[str]:
        comment = None
        if obj.status == QualityIssue.Status.CLOSED.value:
            closing_update = obj.qualityissueupdate_set. \
                filter(new_data__status=QualityIssue.Status.REQUESTING_APPROVAL). \
                order_by('-created_at'). \
                first()

            comment = closing_update.comment if closing_update else ''

        return comment

    def date_of_completion(self, obj: QualityIssue) -> Optional[str]:
        date_of_completion = None
        if obj.status == QualityIssue.Status.CLOSED.value:
            closing_update = obj.qualityissueupdate_set. \
                filter(new_data__status=QualityIssue.Status.CLOSED). \
                order_by('-created_at'). \
                first()

            date_of_completion = closing_update.created_at.strftime(
                '%d %b, %Y') + '\n' + closing_update.created_at.strftime('%I:%M%p') if closing_update else ''

        return date_of_completion

    def created_date(self, obj: QualityIssue) -> str:
        if obj.created_at is None:
            return ''

        created_date = change_timezone_to_london(obj.created_at)

        return self.__get_date_view(created_date)

    def created_time(self, obj: QualityIssue) -> str:
        if obj.created_at is None:
            return ''

        created_date = change_timezone_to_london(obj.created_at)

        return self.__get_time_view(created_date)

    def quality_issue_id(self, obj: QualityIssue) -> str:
        prepared_id = 'QI-%s' % obj.pk

        subtask = obj.subtask_set.order_by('id').first()
        if subtask:
            prepared_id += ' (R-%s)' % subtask.pk

        return prepared_id

    def status_by(self, obj: QualityIssue) -> str:
        history_items = obj.qualityissueupdate_set.all().select_related('user').order_by('created_at')

        result = ''
        serialized_history_items = QualityIssueUpdateSerializer(
            history_items,
            many=True,
            expand=['expanded_user']
        ).data

        for count, item in enumerate(serialized_history_items, start=1):
            status = self.__prepare_status(item)
            result += ('%s) %s %s %s'
                       % (count, item['expanded_user']['first_name'], item['expanded_user']['last_name'], status))

        return result

    def __prepare_status(self, item: dict) -> str:
        status = '/ %s' % self._get_new_data_status(item)
        return self.__add_line_delimiter(status)

    def _get_new_data_status(self, item: dict) -> str:
        new_data_status = item['new_data'].get('status')
        if not new_data_status:
            return ''

        if new_data_status == QualityIssue.Status.DECLINED:
            return 'Subcontractor Declined'

        status = QualityIssue.Status.IN_PROGRESS if new_data_status == QualityIssue.Status.INSPECTION_REJECTED else new_data_status

        return dict(QualityIssue.Status.choices)[status]

    def __add_line_delimiter(self, output) -> str:
        return output + '\n' if self.export_producer == self.ExportProducer.CSV else '<br/>'

    def expanded_response_category(self, obj: QualityIssue) -> str:
        return obj.response_category.name if obj.response_category else ''

    def response_date(self, obj: QualityIssue) -> str:
        if obj.due_date:
            return self.__get_date_view(obj.due_date)
        return ''

    def response_time(self, obj: QualityIssue) -> str:
        if obj.due_date:
            return self.__get_time_view(obj.due_date)
        return ''

    def __get_date_view(self, date: datetime):
        date = change_timezone_to_london(date)
        if self.export_producer == self.ExportProducer.PDF:
            return date.strftime('%d %b, %Y') + '\n' + date.strftime('%I:%M%p')

        return date.strftime('%d/%m/%Y')

    def __get_time_view(self, date: datetime):
        date = change_timezone_to_london(date)
        return date.strftime('%I:%M %p')

    def _get_latest_comment(self, quality_issue: QualityIssue) -> Optional[QualityIssueUpdate]:
        if hasattr(quality_issue, 'latest_comment'):
            return quality_issue.latest_comment[0] if quality_issue.latest_comment else None

        return quality_issue.qualityissueupdate_set.filter(is_comment=True).order_by('-created_at').first()
