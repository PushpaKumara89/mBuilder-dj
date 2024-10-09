from django.db.models import Prefetch, Subquery, Exists, OuterRef
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.task.task_filter import TaskFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import UserSerializer, TaskSerializer
from api.http.serializers.task.task_list_serializer import TaskListSerializer
from api.http.serializers.task.task_restricted_read_serializer import TaskRestrictedReadSerializer
from api.http.views.view import BaseViewSet
from api.models import Task, TaskUpdate, LocationMatrixPackage, Subtask, User
from api.permissions import IsSuperuser, IsProjectClient, IsProjectConsultant
from api.permissions import IsProjectStaff
from api.permissions.is_allowed_for_client import IsAllowedForClient
from api.permissions.is_allowed_for_consultant import IsAllowedForConsultant
from api.permissions.permission_group import PermissionGroup

from api.queues.send_report import send_csv_report, send_pdf_report, send_client_csv_report, send_client_pdf_report
from api.services.task_entity_service import TaskEntityService
from api.utilities.helpers import is_expanded, get_boolean_query_param
from api.utilities.tasks_utilities import modify_queryset, SerializableRequest


class TaskViewSet(BaseViewSet, mixins.UpdateModelMixin, ListModelMixin, mixins.RetrieveModelMixin):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff |
                                             (IsProjectClient & IsAllowedForClient) |
                                             (IsProjectConsultant & IsAllowedForConsultant),),),
        'partial_update': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'update': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'assigned_users': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff, ),),
        'generate_csv': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'generate_pdf': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'generate_client_csv': (IsAuthenticated, IsSuperuser | IsProjectStaff
                                | (IsProjectClient & IsAllowedForClient)
                                | (IsProjectConsultant & IsAllowedForConsultant),),
        'generate_client_pdf': (IsAuthenticated, IsSuperuser | IsProjectStaff
                                | (IsProjectClient & IsAllowedForClient)
                                | (IsProjectConsultant & IsAllowedForConsultant),),
    }

    serializer_class = TaskSerializer
    service = TaskEntityService()
    queryset = Task.objects.all()
    filterset_class = TaskFilter
    search_fields = ['building', 'level', 'area', 'package_activity__name', 'package_activity_task__description',
                     'user__last_name', 'user__first_name', 'user__email', 'taskupdate__recipients__email',
                     'taskupdate__recipients__first_name', 'taskupdate__recipients__last_name']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.service.update(instance, serializer.validated_data)

        return Response(status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.__apply_default_queryset_filters()
        self.serializer_class = TaskListSerializer

        if self.request.user.is_client or self.request.user.is_consultant:
            self.serializer_class = TaskRestrictedReadSerializer
            queryset = queryset.exclude_for_client_report()

        if request.query_params.get('get_total_items_count'):
            return Response({
                'total_items': self.paginator.django_paginator_class(queryset, self.paginator.page_size).get_total_items_count(),
            })

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def generate_csv(self, request, *args, **kwargs):
        project_pk = self.kwargs['project_pk']
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, Task, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def generate_client_csv(self, request, *args, **kwargs):
        project_pk = self.kwargs['project_pk']
        serializable_request = SerializableRequest(request)
        send_client_csv_report(serializable_request, Task, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def generate_client_pdf(self, request, *args, **kwargs):
        project_pk = self.kwargs['project_pk']
        serializable_request = SerializableRequest(request)
        send_client_pdf_report(serializable_request, Task, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def generate_pdf(self, request, *args, **kwargs):
        project_pk = self.kwargs['project_pk']
        serializable_request = SerializableRequest(request)
        send_pdf_report(serializable_request, Task, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def assigned_users(self, request, *args, **kwargs):
        users = User.objects.filter(
            Exists(
                self.filter_queryset(Task.objects.filter(
                    user_id=OuterRef('id'),
                    deleted__isnull=True,
                    project=self.kwargs['project_pk']),
                )
            )
        )
        serializer = UserSerializer(users, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        self.queryset = self.queryset.filter_by_project(self.kwargs)

        self.queryset = self.queryset \
            .select_related('package_activity_task', 'user') \
            .prefetch_related('package_activity__files')

        if is_expanded(self.request, 'expanded_comment'):
            self.queryset = self.queryset.prefetch_related(
                Prefetch(
                    'taskupdate_set',
                    queryset=TaskUpdate.objects.order_by('-created_at'),
                    to_attr='sorted_taskupdate_set'
                )
            )

        if is_expanded(self.request, 'expanded_last_attachments'):
            self.queryset = self.queryset.prefetch_related(
                Prefetch(
                    'taskupdate_set',
                    queryset=TaskUpdate.objects.prefetch_related('files').order_by('-created_at'),
                    to_attr='last_attachments'
                )
            )

        if is_expanded(self.request, 'expanded_user.expanded_user_company'):
            self.queryset = self.queryset.select_related('user__company')

        if is_expanded(self.request, 'expanded_attachments'):
            self.queryset = self.queryset.prefetch_related(
                Prefetch(
                    'location_matrix__locationmatrixpackage_set',
                    queryset=LocationMatrixPackage.all_objects.prefetch_related('media'),
                    to_attr='filtered_locationmatrixpackage_set_with_prefetched_media'
                )
            )

            self.queryset = self.queryset.prefetch_related('package_activity__files')

        if is_expanded(self.request, 'expanded_location_matrix.expanded_project'):
            self.queryset = self.queryset.select_related('location_matrix__project__image')

        if is_expanded(self.request, 'expanded_subtasks.expanded_user') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_task.expanded_location_matrix.expanded_project') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_files') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_company') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_quality_issue.expanded_in_work_subtasks_count') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_quality_issue.expanded_location_matrix.expanded_project') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_quality_issue.expanded_user') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_quality_issue.expanded_attachments') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_last_update.expanded_user') or \
                is_expanded(self.request, 'expanded_subtasks.expanded_last_update.expanded_files'):

            prefetch_subtask_task_queryset = Subtask.objects.get_queryset().prefetch_related('files')

            if is_expanded(self.request, 'expanded_subtasks.expanded_user'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset.select_related('user')

            if is_expanded(self.request, 'expanded_subtasks.expanded_task.expanded_location_matrix.expanded_project'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset.select_related('task__location_matrix__project')

            if is_expanded(self.request, 'expanded_subtasks.expanded_files'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset.prefetch_related('files')

            if is_expanded(self.request, 'expanded_subtasks.expanded_company'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset.select_related('company')

            if is_expanded(self.request, 'expanded_subtasks.expanded_quality_issue.expanded_in_work_subtasks_count'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset \
                    .select_related('quality_issue') \
                    .prefetch_related('quality_issue__attachments')

            if is_expanded(self.request, 'expanded_subtasks.expanded_quality_issue.expanded_location_matrix.expanded_project'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset \
                    .select_related('quality_issue__location_matrix__project__image')

            if is_expanded(self.request, 'expanded_subtasks.expanded_quality_issue.expanded_user'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset \
                    .select_related('quality_issue__user')

            if is_expanded(self.request, 'expanded_subtasks.expanded_quality_issue.expanded_attachments'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset\
                    .select_related('quality_issue') \
                    .prefetch_related('quality_issue__attachments')

            if is_expanded(self.request, 'expanded_subtasks.expanded_last_update.expanded_user') or \
                    is_expanded(self.request, 'expanded_subtasks.expanded_last_update.expanded_files'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset.prefetch_related(
                    'last_update__recipients')

            if is_expanded(self.request, 'expanded_subtasks.expanded_last_update.expanded_user'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset.select_related('last_update__user')

            if is_expanded(self.request, 'expanded_subtasks.expanded_last_update.expanded_files'):
                prefetch_subtask_task_queryset = prefetch_subtask_task_queryset.prefetch_related('last_update__files')

            self.queryset = self.queryset.prefetch_related(
                Prefetch(
                    'subtask_set',
                    queryset=prefetch_subtask_task_queryset
                )
            )

        if get_boolean_query_param(self.request.query_params, 'distinct_by_package_activity_task_name'):
            self.queryset = self.queryset.filter(
                id__in=Subquery(
                    (self.queryset
                     .distinct('package_activity_task_id')
                     .order_by('package_activity_task_id')
                     .values('id'))
                )
            )

        return super().get_queryset()

    def __apply_default_queryset_filters(self):
        self.queryset = modify_queryset(self.queryset, self.request)

        return super().filter_queryset(self.get_queryset())
