import logging
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

import pendulum
import ujson
from django.db.models import Prefetch
from django.http import HttpResponse
from django_filters import rest_framework
from pydash import snake_case
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

from api.http.serializers import LocationMatrixSerializer
from api.http.serializers.project_snapshot.project_snapshot_serializer import ProjectSnapshotSerializer
from api.http.views.mongoengine_view import MongoEngineModelViewSet
from api.models import Project, LocationMatrixPackage, SubtaskUpdate, Subtask, QualityIssueUpdate
from api.models.project_snapshot import ProjectSnapshot
from api.permissions import IsSuperuser
from api.permissions.permission_group import PermissionGroup
from api.permissions.project_snapshot import HasAccess
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_int_array_parameter


class ProjectSnapshotViewSet(MongoEngineModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | HasAccess,),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser,),),
        'destroy': (IsAuthenticated, IsSuperuser,),
        'create': (IsAuthenticated, IsSuperuser,),
        'update': (IsAuthenticated, IsSuperuser,),
    }

    serializer_class = ProjectSnapshotSerializer
    queryset = ProjectSnapshot.objects.all()

    def retrieve(self, request, *args, **kwargs):
        project = get_object_or_404(Project.objects.select_related('image').all(), pk=kwargs['pk'])

        logger = logging.getLogger(__name__)

        try:
            logger.debug(f'In place generation. Start generating snapshot data for project {project.id}.')
            zip_file = self.generate_snapshot(project, request)
            logger.debug(f'In place generation. Finish generating snapshot data for project {project.id}.')
        except BaseException as e:
            logger.exception(repr(e))
            raise e

        response = HttpResponse(zip_file.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={snake_case(project.name)}.zip'

        return response

    def generate_snapshot(self, project: Project, request):
        from api.http.serializers.project_snapshot import ProjectSnapshotDataSerializer
        logger = logging.getLogger(__name__)

        location_matrices_ids = clean_query_param(
            get_int_array_parameter('location_matrix', request.query_params),
            rest_framework.NumberFilter,
            int
        )
        generation_started_at = pendulum.now().to_datetime_string()
        project = Project.objects.prefetch_related(
            'packagematrix_set__package',
            'packagematrix_set__package_activity__files',
            'packagematrix_set__package_activity__packageactivitytask_set',
            'packagematrix_set__companies',
            'packagematrix_set__project',
            'key_contacts',
            'users__company'
        ).filter(id=project.id).get()
        logger.debug('In place generation. Start forming snapshot data. Project %s' % project.pk)
        snapshot_data = ProjectSnapshotDataSerializer(project, expand=['company_admins']).data

        location_matrices_snapshot = []
        location_matrices = project.locationmatrix_set.filter(id__in=location_matrices_ids, deleted__isnull=True).prefetch_related(
            Prefetch('task_set__location_matrix__project__image'),
            Prefetch('task_set__package_activity__files'),
            Prefetch('task_set__package_activity'),
            Prefetch('task_set__package_activity_task'),
            Prefetch('task_set__user'),
            Prefetch(
                'task_set__location_matrix__locationmatrixpackage_set',
                queryset=LocationMatrixPackage.all_objects.select_related('package').order_by('-created_at'),
                to_attr='locationmatrixpackage_set_with_package'
            ),

            Prefetch('task_set__taskupdate_set__user'),
            Prefetch('task_set__taskupdate_set__files__mediathumbnail_set__thumbnail'),
            Prefetch('task_set__taskupdate_set__recipients__user'),

            Prefetch('task_set__subtask_set__company'),
            Prefetch('task_set__subtask_set__files__mediathumbnail_set__thumbnail'),
            Prefetch('task_set__subtask_set__user'),
            Prefetch(
                'task_set__subtask_set__subtaskupdate_set',
                queryset=SubtaskUpdate.objects.filter(
                    new_data__status=Subtask.Status.CLOSED
                ).prefetch_related('files__mediathumbnail_set__thumbnail'),
                to_attr='closed_files_updates'
            ),

            Prefetch('task_set__subtask_set__last_update__files__mediathumbnail_set__thumbnail'),
            Prefetch('task_set__subtask_set__last_update__recipients__user'),
            Prefetch('task_set__subtask_set__last_update__user'),
            Prefetch(
                'task_set__subtask_set__last_update__subtask__subtaskupdate_set',
                queryset=SubtaskUpdate.objects.all().get_with_changed_status_in_desc_order(),
                to_attr='last_updates_with_changed_status'
            ),

            Prefetch('task_set__subtask_set__subtaskupdate_set__recipients__user'),
            Prefetch('task_set__subtask_set__subtaskupdate_set__user'),
            Prefetch('task_set__subtask_set__subtaskupdate_set__files__mediathumbnail_set__thumbnail'),

            Prefetch('qualityissue_set__attachments__mediathumbnail_set__thumbnail'),
            Prefetch('qualityissue_set__user'),
            Prefetch('qualityissue_set__location_matrix'),
            Prefetch('qualityissue_set__old_quality_issue__attachments'),

            Prefetch('qualityissue_set__last_confirmed_update__files__mediathumbnail_set__thumbnail'),
            Prefetch('qualityissue_set__last_confirmed_update__recipients__user'),
            Prefetch('qualityissue_set__last_confirmed_update__user'),

            Prefetch('qualityissue_set__qualityissueupdate_set__files__mediathumbnail_set__thumbnail'),
            Prefetch('qualityissue_set__qualityissueupdate_set__recipients__user'),
            Prefetch('qualityissue_set__qualityissueupdate_set__user'),
            Prefetch(
                'qualityissue_set__qualityissueupdate_set',
                queryset=QualityIssueUpdate.objects.all().get_for_last_recipients().prefetch_related('recipients__user'),
                to_attr='quality_issue_last_recipients'
            ),
            Prefetch(
                'qualityissue_set__qualityissueupdate_set',
                queryset=QualityIssueUpdate.objects.order_by('-created_at').prefetch_related(
                    'recipients__user',
                    'files__mediathumbnail_set__thumbnail',
                ).select_related('user'),
                to_attr='last_updates'
            ),
            Prefetch(
                'qualityissue_set__qualityissueupdate_set',
                queryset=QualityIssueUpdate.objects.all().prefetch_related('recipients', 'files').get_with_changed_status_in_desc_order(),
                to_attr='last_updates_with_changed_status'
            ),

            Prefetch('task_set__subtask_set__last_confirmed_update__files__mediathumbnail_set__thumbnail'),
            Prefetch('task_set__subtask_set__last_confirmed_update__recipients__user'),
            Prefetch('task_set__subtask_set__last_confirmed_update__user'),
            Prefetch(
                'task_set__subtask_set__last_confirmed_update__subtask__subtaskupdate_set',
                queryset=SubtaskUpdate.objects.all().get_with_changed_status_in_desc_order(),
                to_attr='last_updates_with_changed_status'
            ),

            Prefetch('locationmatrixpackage_set__package'),
            Prefetch('locationmatrixpackage_set__media__mediathumbnail_set__thumbnail'),
            Prefetch('locationmatrixpackage_set__package_activity'),
            Prefetch('locationmatrixpackage_set__package_matrix__package'),
            Prefetch('locationmatrixpackage_set__package_matrix__package_activity'),
            Prefetch('locationmatrixpackage_set__package_matrix__package_activity__files'),
            Prefetch('locationmatrixpackage_set__package_matrix__package_activity__packageactivitytask_set'),
            Prefetch('locationmatrixpackage_set__package_matrix__project'),
            Prefetch('locationmatrixpackage_set__package_matrix__companies'),
        ).order_by('id')

        for location_matrix in location_matrices:
            logger.debug('In place generation. Start forming location matrix %s data. Project %s' % (location_matrix.id, project.pk,))

            location_matrix_serializer = LocationMatrixSerializer(location_matrix, expand=[
                'expanded_tasks.expanded_package',
                'expanded_tasks.expanded_location_matrix.expanded_project',

                'expanded_location_matrix_packages.expanded_media.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_location_matrix_packages.expanded_package',
                'expanded_location_matrix_packages.expanded_location_matrix',
                'expanded_location_matrix_packages.expanded_package_activity',

                'expanded_location_matrix_packages.expanded_package_matrix.expanded_project',
                'expanded_location_matrix_packages.expanded_package_matrix.expanded_package',
                'expanded_location_matrix_packages.expanded_package_matrix.expanded_package_activity',
                'expanded_location_matrix_packages.expanded_package_matrix.expanded_companies',

                'expanded_tasks.expanded_updates.expanded_user.expanded_deleted',
                'expanded_tasks.expanded_updates.expanded_files.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_tasks.expanded_updates.expanded_recipients.expanded_user.expanded_deleted',

                'expanded_tasks.expanded_subtasks.expanded_company',
                'expanded_tasks.expanded_subtasks.expanded_user.expanded_deleted',
                'expanded_tasks.expanded_subtasks.expanded_files.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_tasks.expanded_subtasks.expanded_closed_files',
                'expanded_tasks.expanded_subtasks.expanded_location_matrix',

                'expanded_tasks.expanded_subtasks.expanded_last_confirmed_update.expanded_user.expanded_deleted',
                'expanded_tasks.expanded_subtasks.expanded_last_confirmed_update.expanded_previous_status',
                'expanded_tasks.expanded_subtasks.expanded_last_confirmed_update.expanded_files.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_tasks.expanded_subtasks.expanded_last_confirmed_update.expanded_recipients.expanded_user.expanded_deleted',

                'expanded_tasks.expanded_subtasks.expanded_last_update.expanded_user.expanded_deleted',
                'expanded_tasks.expanded_subtasks.expanded_last_update.expanded_previous_status',
                'expanded_tasks.expanded_subtasks.expanded_last_update.expanded_files.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_tasks.expanded_subtasks.expanded_last_update.expanded_recipients.expanded_user',

                'expanded_tasks.expanded_subtasks.expanded_updates.expanded_files.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_tasks.expanded_subtasks.expanded_updates.expanded_user.expanded_deleted',
                'expanded_tasks.expanded_subtasks.expanded_updates.expanded_recipients',
                'expanded_tasks.expanded_subtasks.expanded_updates.expanded_recipients.expanded_user.expanded_deleted',

                'expanded_quality_issues.expanded_user.expanded_deleted',
                'expanded_quality_issues.expanded_attachments.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_quality_issues.expanded_last_status_change_update',
                'expanded_quality_issues.expanded_old_quality_issue',
                'expanded_quality_issues.expanded_last_recipients',
                'expanded_quality_issues.expanded_last_recipients.expanded_user.expanded_deleted',
                'expanded_quality_issues.expanded_location_matrix',
                'expanded_quality_issues.expanded_response_category',
                'expanded_quality_issues.expanded_location_matrix.expanded_project',

                'expanded_quality_issues.expanded_last_confirmed_update.expanded_user.expanded_deleted',
                'expanded_quality_issues.expanded_last_confirmed_update.expanded_files.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_quality_issues.expanded_last_confirmed_update.expanded_recipients.expanded_user.expanded_deleted',

                'expanded_quality_issues.expanded_last_update.expanded_recipients.expanded_user.expanded_deleted',
                'expanded_quality_issues.expanded_last_update.expanded_user.expanded_deleted',
                'expanded_quality_issues.expanded_last_update.expanded_files.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_quality_issues.expanded_last_update.expanded_previous_status',  # Needs to optimize

                'expanded_quality_issues.expanded_updates.expanded_recipients.expanded_user.expanded_deleted',
                'expanded_quality_issues.expanded_updates.expanded_user.expanded_deleted',
                'expanded_quality_issues.expanded_updates.expanded_files.expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_quality_issues.expanded_updates.expanded_previous_status',  # Needs to optimize
            ])
            location_matrices_snapshot.append(location_matrix_serializer.data)

            logger.debug('In place generation. Finish forming location matrix %s data. Project %s' % (location_matrix.id, project.pk,))

        snapshot_data['location_matrix'] = location_matrices_snapshot

        creation_data = {
            'data': snapshot_data,
            'project_id': project.pk,
            'generation_started_at': generation_started_at,
            'created_at': pendulum.now().to_datetime_string(),
            'updated_at': pendulum.now().to_datetime_string(),
        }

        logger.debug('In place generation. Finish forming snapshot data. Project %s' % project.pk)

        file_name = snake_case(project.name)

        logger.debug('In place generation. Start forming zip file with json file inside. Project %s' % project.pk)
        file = BytesIO()
        zf = ZipFile(file, mode="w", compression=ZIP_DEFLATED)
        zf.writestr(f'{file_name}.json', ujson.dumps(creation_data))
        zf.close()
        logger.debug('In place generation. Finish forming zip file with json file inside. Project %s' % project.pk)

        return file
