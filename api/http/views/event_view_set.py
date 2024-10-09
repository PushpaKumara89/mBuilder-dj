from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from api.http.serializers.event.event_create_serializer import EventCreateSerializer
from api.http.serializers.event.event_serializer import EventSerializer
from api.http.views.mongoengine_view import MongoEngineModelViewSet
from api.models import Event, Project
from api.permissions import IsSuperuser
from api.permissions.events import IsProjectUser
from api.permissions.permission_group import PermissionGroup


class EventViewSet(MongoEngineModelViewSet):
    _request_permissions = {
        'create': (IsAuthenticated, IsSuperuser | IsProjectUser,),
        'list': (HasAPIKey | PermissionGroup(IsAuthenticated, IsSuperuser | IsProjectUser),),
    }

    serializer_class = EventSerializer
    queryset = Event.objects().order_by('created_at')

    def create(self, request, *args, **kwargs):
        serializer = EventCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_serializer = self.get_serializer(data=serializer.initial_data['events'], many=True)
        event_serializer.is_valid(raise_exception=True)

        self.perform_create(event_serializer)
        headers = self.get_success_headers(event_serializer.data)
        return Response(event_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs['pk'])
        query_params = request.query_params

        if 'processed_from' in query_params:
            self.queryset = self.queryset.filter(created_at__gt=query_params['processed_from'], project_id=project.pk)

        return super().list(request, *args, **kwargs)
