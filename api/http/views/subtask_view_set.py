from functools import reduce

from django.db.models import Prefetch, Q, CharField, Count
from django.db.models.expressions import RawSQL, Value, Subquery, Exists, OuterRef
from django.db.models.functions import Concat
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from api.http.filters.subtask import SubtaskFilter
from api.http.mixins import ListModelMixin
from api.http.serializers import UserSerializer, SubtaskSerializer, SubtaskFilesSerializer, SubtaskCountSerializer, \
    SubtaskBulkCreateSerializer, SubtaskBulkCreateFromQualityIssueSerializer, CompanySerializer
from api.http.views.view import BaseViewSet
from api.models import Subtask, SubtaskUpdate, Company, User
from api.models.queryset import SafeDeleteQueryset
from api.permissions import IsProjectStaff, IsSubcontractor, IsSuperuser, IsProjectUser, IsProjectSubcontractor
from api.permissions.subtasks.can_client_see_project_subtasks import CanClientSeeProjectSubtasks
from api.permissions.permission_group import PermissionGroup

from api.queues.send_report import send_csv_report, send_pdf_report
from api.services.subtask_entity_service import SubtaskEntityService
from api.utilities.helpers import is_expanded
from api.utilities.subtask_utilities import apply_default_ordering, apply_common_filters_queryset
from api.utilities.tasks_utilities import SerializableRequest


class SubtaskViewSet(BaseViewSet, ListModelMixin, ModelViewSet):
    _request_permissions = {
        'retrieve': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectSubcontractor),),
        'create': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'bulk_create_from_tasks': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'bulk_create_from_quality_issues': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'destroy': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | CanClientSeeProjectSubtasks | IsProjectSubcontractor),),
        'creators': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectSubcontractor),),
        'companies': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | IsProjectSubcontractor),),
        'add_files': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'remove_files': (IsAuthenticated, IsSuperuser | IsProjectStaff,),
        'generate_csv': (IsAuthenticated, IsSuperuser | IsProjectStaff | IsSubcontractor,),
        'generate_pdf': (IsAuthenticated, IsSuperuser | IsProjectStaff | IsSubcontractor,),
        'count': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectUser, ),),
        'retrieve_files': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectStaff | CanClientSeeProjectSubtasks | IsProjectSubcontractor),),
    }

    serializer_class = SubtaskSerializer
    service = SubtaskEntityService()
    queryset = Subtask.objects.all()
    filterset_class = SubtaskFilter
    search_fields = ['id', 'description', 'task__location_matrix__building', 'task__location_matrix__level',
                     'task__location_matrix__area', 'task__package_activity__name',
                     'task__package_activity_task__description', 'user__last_name', 'user__first_name', 'user__email',
                     'subtaskupdate__recipients__email', 'subtaskupdate__recipients__first_name',
                     'subtaskupdate__recipients__last_name']

    def get_queryset(self, filter_subcontractors=True):
        queryset = apply_common_filters_queryset(self.queryset, self.request, self.kwargs, filter_subcontractors)
        queryset = self._fetch_expanded_fields_relations(queryset)
        if self.request.user.is_client:
            queryset = queryset.filter(quality_issue__isnull=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.add_default_ordering()

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

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk

        # for older versions of iOS app
        if request.data.get('recipients'):
            for recipient_index, recipient in enumerate(request.data['recipients']):
                user_id = recipient.get('user_id')
                if user_id is not None:
                    del request.data['recipients'][recipient_index]['user_id']
                    request.data['recipients'][recipient_index]['user'] = user_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.service.create(validated_data=serializer.validated_data, user=request.user)

        return Response(data=self.get_serializer(result).data, status=status.HTTP_201_CREATED)

    def bulk_create_from_tasks(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        serializer = SubtaskBulkCreateSerializer(
            data=request.data,
            context={'project_pk': kwargs['project_pk'], 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.service.bulk_create_from_tasks(validated_data=serializer.validated_data, user=request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def bulk_create_from_quality_issues(self, request, *args, **kwargs):
        request.data['user'] = request.user.pk
        serializer = SubtaskBulkCreateFromQualityIssueSerializer(
            data=request.data,
            context={'project_pk': kwargs['project_pk'], 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.service.bulk_create_from_quality_issues(validated_data=serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        self.service.after_destroy(instance)

        return response

    def add_files(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SubtaskFilesSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.add()

        return Response(status=status.HTTP_200_OK)

    def remove_files(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SubtaskFilesSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.remove()

        return Response(status=status.HTTP_200_OK)

    def generate_csv(self, request, *args, **kwargs):
        project_pk = self.kwargs['project_pk']
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, Subtask, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def generate_pdf(self, request, *args, **kwargs):
        project_pk = self.kwargs['project_pk']
        serializable_request = SerializableRequest(request)
        send_pdf_report(serializable_request, Subtask, project_pk, request.user.email)

        return Response(status=status.HTTP_200_OK)

    def count(self, request, *args, **kwargs):
        total_all = 0
        statuses_count = {subtask_status: 0 for subtask_status in Subtask.Status.values}

        if self.filter_queryset(self.get_queryset()).exists():
            grouped_statuses = Subtask.objects.filter(id__in=Subquery(self.filter_queryset(self.get_queryset().values('id')))).values('status').annotate(status_count=Count('id')).order_by('status', with_default_order=False)
            total_all = reduce(lambda s1, s2: s1 + s2['status_count'], list(grouped_statuses), 0)
            for status_stats in grouped_statuses:
                statuses_count[status_stats['status']] = status_stats['status_count']

        serializer = SubtaskCountSerializer({
            'total': total_all,
            **statuses_count
        })

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def creators(self, request, *args, **kwargs):
        users = User.objects.filter(
            Exists(self.filter_queryset(queryset=self.get_queryset(False).filter(user=OuterRef('id'))))
        )
        serializer = UserSerializer(users, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def companies(self, request, *args, **kwargs):
        companies = Company.objects.filter(Exists(
            self.filter_queryset(queryset=self.get_queryset(filter_subcontractors=False).filter(company=OuterRef('id'))))
        )
        serializer = CompanySerializer(companies, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve_files(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, expand=[
            'expanded_closed_files',
            'expanded_files.expanded_thumbnails.expanded_thumbnail'
        ], fields=[
            'expanded_closed_files',
            'expanded_files'
        ])
        return Response(serializer.data)

    def add_default_ordering(self):
        queryset = apply_default_ordering(self.get_queryset(), self.request)

        return super().filter_queryset(queryset)

    def _fetch_expanded_fields_relations(self, queryset: SafeDeleteQueryset) -> SafeDeleteQueryset:
        select_related = ['company', 'task__user', 'task__package_activity_task', 'user__company']
        prefetch_related = ['files', 'task__package_activity__files']

        self._fetch_subtask(prefetch_related=prefetch_related)
        self._fetch_task(prefetch_related=prefetch_related, select_related=select_related)
        self._fetch_quality_issue(prefetch_related=prefetch_related, select_related=select_related)
        self._fetch_last_update(prefetch_related=prefetch_related, select_related=select_related)
        self._fetch_last_confirmed_update(prefetch_related=prefetch_related, select_related=select_related)

        return queryset.select_related(*set(select_related)).prefetch_related(*set(prefetch_related))

    def _fetch_last_update(self, prefetch_related: list, select_related: list) -> None:
        if is_expanded(self.request, 'expanded_last_update.expanded_user') or is_expanded(self.request, 'expanded_last_update.expanded_files'):
            prefetch_related.extend(['last_update__files', 'last_update__recipients__user'])

        if is_expanded(self.request, 'expanded_last_update.expanded_user'):
            select_related.append('last_update__user')

    def _fetch_quality_issue(self, prefetch_related: list, select_related: list) -> None:
        if is_expanded(self.request, 'expanded_quality_issue.expanded_location_matrix.expanded_project'):
            select_related.append('quality_issue__location_matrix__project__image')

        if is_expanded(self.request, 'expanded_quality_issue.expanded_in_work_subtasks_count'):
            prefetch_related.append(
                Prefetch('quality_issue__subtask_set',
                         queryset=Subtask.objects.filter(status__in=[Subtask.Status.CONTESTED, Subtask.Status.INSPECTION_REJECTED,
                                                                     Subtask.Status.IN_PROGRESS, Subtask.Status.UNDER_INSPECTION]),
                         to_attr='opened_subtasks')
            )

        if is_expanded(self.request, 'expanded_quality_issue.expanded_user'):
            select_related.append('quality_issue__user')

        if is_expanded(self.request, 'expanded_quality_issue.expanded_attachments'):
            prefetch_related.append('quality_issue__attachments')

        if prefetch_related or select_related:
            prefetch_related.append('quality_issue__attachments')

    def _fetch_subtask(self, prefetch_related: list) -> None:
        if is_expanded(self.request, 'expanded_last_recipients'):
            prefetch_related.append(
                Prefetch('subtaskupdate_set',
                         queryset=(SubtaskUpdate.objects
                                   .annotate(transition=Concat(RawSQL('old_data ->> %s', ('status',)),
                                                               Value('-'),
                                                               RawSQL('new_data ->> %s', ('status',)),
                                                               output_field=CharField()))
                                   .filter(Q(transition=f'{Subtask.Status.IN_PROGRESS}-{Subtask.Status.IN_PROGRESS}')
                                           | Q(transition=f'{Subtask.Status.CONTESTED}-{Subtask.Status.IN_PROGRESS}')
                                           | Q(transition=f'-{Subtask.Status.IN_PROGRESS}'))
                                   .order_by('-created_at')
                                   .prefetch_related('files')),
                         to_attr='last_recipients_updates')
            )

        if is_expanded(self.request, 'expanded_closed_files'):
            prefetch_related.append(
                Prefetch('subtaskupdate_set',
                         queryset=(SubtaskUpdate.objects
                                   .filter(new_data__status=Subtask.Status.CLOSED)
                                   .prefetch_related('files')),
                         to_attr='closed_files_updates')
            )

        if is_expanded(self.request, 'expanded_status_date') or is_expanded(self.request, 'expanded_last_status_change_update'):
            prefetch_related.append(
                Prefetch('subtaskupdate_set',
                         queryset=(SubtaskUpdate.objects
                                   .filter(~Q(old_data__status=RawSQL('new_data -> %s', ('status',))))
                                   .order_by('-created_at')),
                         to_attr='last_status_change_update')
            )

    def _fetch_task(self, prefetch_related: list, select_related: list) -> None:
        if is_expanded(self.request, 'expanded_task.expanded_location_matrix.expanded_project'):
            select_related.append('task__location_matrix__project__image')

    def _fetch_last_confirmed_update(self, prefetch_related: list, select_related: list) -> None:
        if is_expanded(self.request, 'expanded_last_confirmed_update.expanded_files'):
            prefetch_related.append('last_confirmed_update__files')

        if is_expanded(self.request, 'expanded_last_confirmed_update.expanded_user'):
            select_related.append('last_confirmed_update__user')

        if select_related or prefetch_related:
            prefetch_related.extend(['last_confirmed_update__files', 'last_confirmed_update__recipients'])
