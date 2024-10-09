from datetime import datetime
from enum import Enum

from django.core.files.storage import default_storage

from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import fields, serializers

from api.http.serializers import UserSerializer, PackageActivitySerializer
from api.http.serializers.location_matrix.location_matrix_serializer import LocationMatrixSerializer
from api.http.serializers.package_activity_tasks import PackageActivityTaskSerializer
from api.http.serializers.task.task_status_history_serializer import TaskStatusHistorySerializer
from api.models import Task, PackageMatrixHiddenActivityTask, Media
from django.conf import settings

from api.utilities.time_utilities import change_timezone_to_london


class TasksReportSerializer(FlexFieldsModelSerializer):
    class ExportProducer(Enum):
        CSV = 1
        PDF = 2

    class Meta:
        model = Task
        fields = (
            'id', 'status', 'package_activity', 'package_activity_task',
            'location_matrix', 'user', 'created_at', 'updated_at'
        )
        expandable_fields = {
            'expanded_date_accepted': (serializers.SerializerMethodField, {'method_name': 'date_accepted'}),
            'expanded_time_accepted': (serializers.SerializerMethodField, {'method_name': 'time_accepted'}),
            'expanded_quality_critical_task_id': (serializers.SerializerMethodField, {'method_name': 'quality_critical_task_id'}),
            'expanded_project_number': (serializers.SerializerMethodField, {'method_name': 'project_number'}),
            'expanded_package': (serializers.SerializerMethodField, {'method_name': 'package'}),
            'expanded_package_activity_name': (serializers.SerializerMethodField, {'method_name': 'package_activity_name'}),
            'expanded_package_activity_id': (serializers.SerializerMethodField, {'method_name': 'package_activity_id'}),
            'expanded_package_activity_is_hidden': (serializers.SerializerMethodField, {'method_name': 'package_activity_is_hidden'}),
            'expanded_package_activity_task_description': (serializers.SerializerMethodField, {'method_name': 'package_activity_task_description'}),
            'expanded_building': (serializers.SerializerMethodField, {'method_name': 'building'}),
            'expanded_level': (serializers.SerializerMethodField, {'method_name': 'level'}),
            'expanded_area': (serializers.SerializerMethodField, {'method_name': 'area'}),
            'expanded_status_by': (serializers.SerializerMethodField, {'method_name': 'status_by'}),
            'expanded_comments': (serializers.SerializerMethodField, {'method_name': 'comments'}),
            'expanded_recipients': (serializers.SerializerMethodField, {'method_name': 'recipients'}),
            'expanded_image_urls': (serializers.SerializerMethodField, {'method_name': 'image_urls'}),
            'expanded_attachments': (serializers.SerializerMethodField, {'method_name': 'attachments'}),
            'expanded_initial_status_date': (serializers.SerializerMethodField, {'method_name': 'initial_status_date'}),
            'expanded_initial_status_time': (serializers.SerializerMethodField, {'method_name': 'initial_status_time'}),
            'expanded_last_update_date': (serializers.SerializerMethodField, {'method_name': 'last_update_date'}),
            'expanded_last_update_time': (serializers.SerializerMethodField, {'method_name': 'last_update_time'}),
            'expanded_first_update_date': (serializers.SerializerMethodField, {'method_name': 'first_update_date'}),
            'expanded_first_update_time': (serializers.SerializerMethodField, {'method_name': 'first_update_time'})
        }

    package_activity = PackageActivitySerializer(omit=['package_activity_tasks'])
    package_activity_task = PackageActivityTaskSerializer()
    location_matrix = LocationMatrixSerializer()
    status = fields.ChoiceField(choices=Task.Statuses.choices, source='get_status_display')
    user = UserSerializer()

    created_at = fields.DateTimeField(read_only=True, format=settings.DATE_FORMAT)
    updated_at = fields.DateTimeField(read_only=True, format=settings.DATE_FORMAT)

    def __init__(self, *args, export_producer: ExportProducer = ExportProducer.PDF, **kwargs):
        self.export_producer = export_producer

        super().__init__(*args, **kwargs)

    def last_update_date(self, obj: Task):
        updated_at = change_timezone_to_london(obj.updated_at)

        return self.__get_date_view(updated_at)

    def last_update_time(self, obj: Task):
        updated_at = change_timezone_to_london(obj.updated_at)

        return self.__get_time_view(updated_at)

    def first_update_date(self, obj: Task):
        first_update_after_initial = list(obj.taskupdate_set.order_by('created_at').all()[1:2])

        if not first_update_after_initial:
            return None

        first_update_after_initial = first_update_after_initial[0]

        first_update_date = change_timezone_to_london(first_update_after_initial.created_at)

        return self.__get_date_view(first_update_date)

    def first_update_time(self, obj: Task):
        first_update_after_initial = list(obj.taskupdate_set.order_by('created_at').all()[1:2])

        if not first_update_after_initial:
            return None

        first_update_after_initial = first_update_after_initial[0]

        first_update_date = change_timezone_to_london(first_update_after_initial.created_at)

        return self.__get_time_view(first_update_date)

    def date_accepted(self, obj: Task):
        if self.export_producer == self.ExportProducer.CSV:
            history_items = obj.taskupdate_set.all().order_by('created_at')

            result = ''
            for count, item in enumerate(history_items, start=1):
                date = change_timezone_to_london(item.created_at)
                result += '%s) %s \n' % (count, self.__get_date_view(date))

            return result

        if obj.date_of_approval is None:
            return ''

        date_of_approval = change_timezone_to_london(obj.date_of_approval)

        return self.__get_date_view(date_of_approval)

    def time_accepted(self, obj: Task):
        if self.export_producer == self.ExportProducer.CSV:
            history_items = obj.taskupdate_set.all().order_by('created_at')

            result = ''
            for count, item in enumerate(history_items, start=1):
                date = change_timezone_to_london(item.created_at)
                result += '%s) %s \n' % (count, self.__get_time_view(date))

            return result

        if obj.date_of_approval is None:
            return ''

        date_of_approval = change_timezone_to_london(obj.date_of_approval)

        return self.__get_time_view(date_of_approval)

    def initial_status_date(self, obj: Task):
        if obj.created_at is None:
            return ''

        initial_status_date = change_timezone_to_london(obj.updated_at)

        return self.__get_date_view(initial_status_date)

    def initial_status_time(self, obj: Task):
        if obj.created_at is None:
            return ''

        initial_status_date = change_timezone_to_london(obj.updated_at)

        return self.__get_time_view(initial_status_date)

    def package(self, obj: Task):
        location_matrix_package = obj.location_matrix.locationmatrixpackage_set.filter(
            package_activity=obj.package_activity
        ).select_related('package').first()
        return '' if location_matrix_package is None else location_matrix_package.package.name

    def quality_critical_task_id(self, obj: Task):
        return 'QCT-%s' % obj.pk

    def project_number(self, obj: Task):
        return obj.location_matrix.project.number

    def package_activity_name(self, obj: Task):
        return obj.package_activity.name

    def package_activity_id(self, obj: Task):
        return obj.package_activity.activity_id or ''

    def package_activity_is_hidden(self, obj: Task):
        return PackageMatrixHiddenActivityTask.objects.filter(
                package_activity_task_id=obj.package_activity_task_id,
                package_matrix__project_id=obj.project_id
            ).exists()

    def package_activity_task_description(self, obj: Task):
        return obj.package_activity_task.description

    def building(self, obj: Task):
        return obj.location_matrix.building

    def level(self, obj: Task):
        return obj.location_matrix.level

    def area(self, obj: Task):
        return obj.location_matrix.area

    def status_by(self, obj: Task):
        history_items = obj.taskupdate_set.all().select_related('user').order_by('created_at')

        result = ''
        serialized_history_items = TaskStatusHistorySerializer(history_items, many=True).data
        for count, item in enumerate(serialized_history_items, start=1):
            status = '/ %s' % item['status'] if self.export_producer == 'csv' else ''

            result += '%s) %s %s %s\n' % (count, item['user']['first_name'], item['user']['last_name'], status)

        return result

    def comments(self, obj: Task):
        if self.export_producer == self.ExportProducer.CSV:
            history_items = obj.taskupdate_set.all().order_by('created_at')

            result = ''
            serialized_history_items = TaskStatusHistorySerializer(history_items, many=True).data
            for count, item in enumerate(serialized_history_items, start=1):
                result += '%s) %s\n' % (count, item['comment'])

            return result

        last_update = obj.taskupdate_set.all().order_by('-created_at').first()

        return last_update.comment if last_update else ''

    def recipients(self, obj: Task):
        update_history = obj.taskupdate_set.all().order_by('created_at')
        result = ''

        for count, update in enumerate(update_history, start=1):
            recipients = [recipient.email for recipient in update.recipients.all()]
            result += '%s) %s\n' % (count, ', '.join(recipients))

        return result

    def attachments(self, obj: Task):
        last_update = obj.taskupdate_set.prefetch_related('files').all().order_by('-created_at').first()

        if last_update is None:
            return []

        return [self.__generate_image_link(media) for media in last_update.files.all()]

    def image_urls(self, obj: Task):
        if self.export_producer == self.ExportProducer.CSV:
            history_items = obj.taskupdate_set.prefetch_related('files').all().order_by('created_at')
            result = ''

            for count, item in enumerate(history_items, start=1):
                files = [self.__generate_image_url(media) for media in item.files.all()]
                result += '%s) %s\n' % (count, ', '.join(files))

            return result

        last_update = obj.taskupdate_set.prefetch_related('files').all().order_by('-created_at').first()

        if last_update is None:
            return ''

        files = [self.__generate_image_url(media) for media in last_update.files.all()]

        return '%s\n' % ', '.join(files)

    def __generate_image_link(self, media: Media) -> dict:
        return {
            'link': default_storage.url(media.name) if media.is_public else media.link,
            'name': media.name
        }

    def __generate_image_url(self, media: Media) -> str:
        return default_storage.url(media.name) if media.is_public else media.link

    def __get_date_view(self, date: datetime) -> str:
        date = change_timezone_to_london(date)
        if self.export_producer == self.ExportProducer.PDF:
            return date.strftime('%d %b, %Y') + '\n' + date.strftime('%I:%M%p')

        return date.strftime('%d/%m/%Y')

    def __get_time_view(self, created_at: datetime) -> str:
        created_date = change_timezone_to_london(created_at)
        return created_date.strftime('%I:%M %p')
