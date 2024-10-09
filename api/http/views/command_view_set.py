import logging

from django.conf import settings
from django_filters import rest_framework
from django_rq import get_connection
from mongoengine import NotUniqueError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rq import Queue, Worker

from api.http.serializers import CommandSerializer
from api.http.views.mongoengine_view import MongoEngineModelViewSet
from api.models import Command, Project
from api.permissions import IsSuperuser
from api.permissions.events import IsProjectUser
from api.commands import process_commands
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_array_parameter


logger = logging.getLogger(__name__)


class CommandViewSet(MongoEngineModelViewSet):
    _request_permissions = {
        'create': (IsAuthenticated, IsSuperuser | IsProjectUser,),
        'list': (IsAuthenticated, IsSuperuser | IsProjectUser,),
    }

    serializer_class = CommandSerializer
    queryset = Command.objects.all()

    def list(self, request, *args, **kwargs):
        project = get_object_or_404(queryset=Project.objects.all(), pk=kwargs['pk'])
        local_id_filter = clean_query_param(
            get_array_parameter('local_id', request.query_params),
            rest_framework.CharFilter
        )
        query_filters = {'project_id': project.id}

        if local_id_filter:
            query_filters['data__local_id__in'] = local_id_filter

        self.queryset = self.queryset.filter(**query_filters)

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Process each command separately to save their order.
        commands = []
        logger.debug('Commands')
        logger.debug(request.data.get('commands', []))
        for command in request.data.get('commands', []):
            logger.debug('Process command')
            logger.debug(command)
            serializer = self.get_serializer(data=command)
            serializer.is_valid(raise_exception=True)

            try:
                new_command = serializer.create(serializer.validated_data)
            except NotUniqueError as exc:
                raise ValidationError(str(exc))

            commands.append(new_command)

        queue_name = 'commands-project-*'
        redis_connection = get_connection(queue_name)
        logger.warning('Redis connection ' + repr(redis_connection))
        workers = Worker.all(connection=redis_connection)
        worker_dicts = []
        for worker in workers:
            worker_dicts.append({
                'birth_date': str(worker.birth_date),
                'connection': repr(worker.connection),
                'name': worker.name,
                'key': worker.key,
                'death_date': str(worker.death_date)
            })

        logger.warning('Workers: ' + str(worker_dicts))
        queue = Queue(queue_name.replace('*', str(kwargs['pk'])), connection=redis_connection,
                      is_async=settings.RQ_QUEUES[queue_name].get('ASYNC', True))
        queue.enqueue(process_commands, commands)

        return Response(request.data.get('commands', []), status=status.HTTP_201_CREATED)
