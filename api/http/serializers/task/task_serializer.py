from rest_framework import fields
from rest_framework import serializers
from api.http.serializers import UserSerializer, PackageActivitySerializer, PackageSerializer, MediaSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.location_matrix.location_matrix_serializer import LocationMatrixSerializer
from api.http.serializers.package_activity_tasks import PackageActivityTaskSerializer
from api.http.serializers.task_update.task_update_serializer import TaskUpdateSerializer
from api.models import Task


class TaskSerializer(BaseModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id', 'status', 'package_activity', 'package_activity_task', 'local_id',
            'location_matrix', 'user', 'date_of_approval', 'created_at', 'updated_at',
        )
        expandable_fields = {
            'expanded_subtasks': ('api.http.serializers.SubtaskSerializer', {'many': True, 'source': 'subtask_set'}),
            'expanded_attachments': (serializers.SerializerMethodField, {'method_name': 'attachments'}),
            'expanded_comment': (serializers.SerializerMethodField, {'method_name': 'comment'}),
            'expanded_location_matrix': (LocationMatrixSerializer, {'source': 'location_matrix'}),
            'expanded_package': (serializers.SerializerMethodField, {'method_name': 'package'}),
            'expanded_last_attachments': (serializers.SerializerMethodField, {'method_name': 'get_last_attachments'}),
            'expanded_updates': (TaskUpdateSerializer, {'many': True, 'source': 'taskupdate_set'}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_package_activity': (PackageActivitySerializer, {'source': 'package_activity'})
        }

    package_activity = PackageActivitySerializer(omit=['package_activity_tasks'])
    package_activity_task = PackageActivityTaskSerializer()
    location_matrix = LocationMatrixSerializer()
    status = fields.ChoiceField(choices=Task.Statuses.choices)
    user = UserSerializer()
    date_of_approval = fields.DateTimeField(read_only=True)
    local_id = serializers.CharField(required=False, max_length=255, allow_null=True, allow_blank=True)

    def package(self, obj: Task):
        if hasattr(obj.location_matrix, 'locationmatrixpackage_set_with_package'):
            location_matrix_package = next(filter(lambda lmp: lmp.package_activity_id == obj.package_activity_id,
                                                  obj.location_matrix.locationmatrixpackage_set_with_package))
            location_matrix_package = location_matrix_package if location_matrix_package else None
        else:
            location_matrix_package = obj.location_matrix.locationmatrixpackage_set.all_with_deleted().select_related('package').filter(
                package_activity=obj.package_activity
            ).first()

        if location_matrix_package:
            return PackageSerializer(location_matrix_package.package).data

        return None

    def attachments(self, obj: Task):
        attachments = list(obj.package_activity.files.all())
        if hasattr(obj.location_matrix, 'filtered_locationmatrixpackage_set_with_prefetched_media'):
            location_matrix_package = next(filter(lambda lmp: lmp.package_activity_id == obj.package_activity_id,
                                                  obj.location_matrix.filtered_locationmatrixpackage_set_with_prefetched_media))

            attachments += list(location_matrix_package.media.all())

        return MediaSerializer(attachments, many=True).data

    def comment(self, obj: Task):
        if hasattr(obj, 'sorted_taskupdate_set'):
            last_task_update = obj.sorted_taskupdate_set[0] if obj.sorted_taskupdate_set else None
        else:
            last_task_update = obj.taskupdate_set.order_by('-created_at').first()

        return last_task_update.comment if last_task_update else ''

    def get_last_attachments(self, obj: Task):
        if hasattr(obj, 'last_attachments'):
            files = obj.last_attachments[0].files.all() if obj.last_attachments else []
        else:
            files = obj.taskupdate_set.prefetch_related('files').order_by('-created_at').first().files.all()

        return MediaSerializer(files, many=True, expand=['expanded_thumbnails.expanded_thumbnail']).data
