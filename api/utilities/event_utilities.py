import pendulum
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from safedelete.models import is_safedelete_cls
from typing import Optional

from api.http.serializers import LocationMatrixPackagesSerializer, ProjectSerializer, ProjectNewsSerializer, \
    SubtaskSerializer, SubtaskUpdateSerializer, PackageActivitySerializer, ProjectUserSerializer, RecipientSerializer, \
    TaskSerializer, MediaSerializer, PackageSerializer, CompanySerializer, PackageMatrixCompanySerializer, \
    QualityIssueSerializer, QualityIssueUpdateSerializer, ResponseCategorySerializer
from api.http.serializers.location_matrix.location_matrix_serializer import LocationMatrixSerializer
from api.http.serializers.media_thumbnail.media_thumbnail_serializer import MediaThumbnailSerializer
from api.http.serializers.package_activity_tasks import PackageActivityTaskSerializer
from api.http.serializers.package_matrix.package_matrix_serializer import PackageMatrixSerializer
from api.http.serializers.package_matrix_hidden_activity_task_serializer import \
    PackageMatrixHiddenActivityTaskSerializer
from api.http.serializers.task_update.task_update_serializer import TaskUpdateSerializer
from api.http.serializers.user.user_serializer import UserSerializer
from api.models import Event
from api.models.managers import BaseManager


def perform_event_creation(parent_entity_field: str, child_entity_field: str, entity_name: str, kwargs):
    def form_m2m_data():
        if is_safedelete_cls(kwargs['model']):
            child_entities = kwargs['model'].all_objects.filter(pk__in=kwargs['pk_set']).all()
        else:
            child_entities = kwargs['model'].objects.filter(pk__in=kwargs['pk_set']).all()

        m2m_data = []
        for entity in child_entities:
            mapping = model_serialization_map(entity)
            child_entity = dict(sorted(mapping['serializer'](entity, expand=mapping['expand']).data.items()))

            m2m_data.append({
                parent_entity_field: kwargs.get('instance').pk,
                child_entity_field: dict(child_entity)
            })

        return m2m_data

    if not kwargs.get('reverse'):
        project_id = get_project_id(kwargs.get('instance'))

        if kwargs.get('action') == 'post_add':
            data = form_m2m_data()

            create_events_for_m2m_post_add(entity_name, project_id, data)
        elif kwargs.get('action') == 'post_remove':
            data = form_m2m_data()

            create_events_for_m2m_post_remove(entity_name, project_id, data)


def perform_group_event_creation(entity_name: str, kwargs):
    def form_m2m_data():
        child_entities = kwargs['model'].objects.filter(pk__in=kwargs['pk_set']).all()

        m2m_data = []
        for entity in child_entities:
            child_entity = model_to_dict(entity)

            m2m_data.append({
                'user': kwargs.get('instance').pk,
                'group': child_entity
            })

        return m2m_data

    if not kwargs.get('reverse'):
        project_id = get_project_id(kwargs.get('instance'))

        if kwargs.get('action') == 'post_add':
            data = form_m2m_data()
            create_events_for_m2m_post_add(entity_name, project_id, data)
        elif kwargs.get('action') == 'post_remove':
            data = form_m2m_data()
            create_events_for_m2m_post_remove(entity_name, project_id, data)


# Create events for signals
def create_events_for_bulk_post_save(**kwargs):
    instances = kwargs.get('instances', [])
    is_creation = kwargs.get('created')

    updated_fields = kwargs.get('update_fields', [])
    updated_fields = updated_fields if type(updated_fields) in [list, frozenset, set] else []

    entity_name = instances[0].get_snake_case_class_name()
    event_type = define_event_type(instances[0], is_creation, updated_fields)

    create_events(instances, event_type, entity_name, kwargs.get('project_id'))


def create_events_for_post_update(**kwargs):
    entities = kwargs.get('instances')

    update_fields = kwargs.get('update_fields')
    update_fields = update_fields if type(update_fields) is dict else {}

    entity_name = entities[0].get_snake_case_class_name()
    event_type = define_event_type_for_update(update_fields)
    project_id = get_project_id(entities[0])

    create_events(entities, event_type, entity_name, project_id)


def create_events_for_post_delete(**kwargs):
    instances = kwargs.get('instances', [])
    entity_name = instances[0].get_snake_case_class_name()

    event_type = Event.Types.ENTITY_DELETED
    create_events(instances, event_type, entity_name, kwargs.get('project_id'))


def create_events_for_project_m2m_reverse_post_delete(entities: list, entity_name: str):
    event_type = Event.Types.ENTITY_DELETED

    events = list()
    time = pendulum.now().to_datetime_string()
    for entity in entities:
        events.append(Event(
            data=entity,
            entity=entity_name,
            type=event_type.value,
            created_at=time,
            updated_at=time,
            project_id=entity['project']
        ))

    if len(events) > 0:
        return Event.objects.insert(events)


def create_events_for_m2m_post_add(entity_name: str, project_id: int, data: list):
    event_type = Event.Types.ENTITY_CREATED

    create_events(data, event_type, entity_name, project_id)


def create_events_for_m2m_post_remove(entity_name: str, project_id: int, data: list):
    event_type = Event.Types.ENTITY_DELETED

    create_events(data, event_type, entity_name, project_id)


def define_event_type_for_update(updated_fields):
    if 'deleted' in updated_fields and updated_fields['deleted']:
        event_type = Event.Types.ENTITY_DELETED
    elif 'deleted' in updated_fields and not updated_fields['deleted']:
        event_type = Event.Types.ENTITY_RESTORED
    else:
        event_type = Event.Types.ENTITY_UPDATED

    return event_type


def define_event_type(obj, is_creation, updated_fields: dict) -> Event.Types:
    if is_creation:
        event_type = Event.Types.ENTITY_CREATED
    elif not updated_fields:
        event_type = Event.Types.ENTITY_RESTORED
    elif 'deleted' in updated_fields and obj.deleted is not None:
        event_type = Event.Types.ENTITY_DELETED
    elif 'deleted' in updated_fields and obj.deleted is None:
        event_type = Event.Types.ENTITY_RESTORED
    else:
        event_type = Event.Types.ENTITY_UPDATED

    return event_type


def create_events(entities: list, event_type: Event.Types, entity_name: str, project_id: int = None) -> None:
    events = list()
    time = pendulum.now()
    for entity in entities:
        if type(entity) is not dict:
            serialization_map = model_serialization_map(entity)
            if not serialization_map:
                continue

            entity = dict(sorted(serialization_map['serializer'](entity, expand=serialization_map['expand']).data.items()))

        events.append(Event(
            data=entity,
            entity=entity_name,
            type=event_type.value,
            created_at=time,
            updated_at=time,
            project_id=project_id
        ))

    if events:
        return Event.objects.insert(events)


def project_field_path(instance) -> Optional[list[str]]:
    field_map = {
        'location_matrix': [['project_id']],
        'location_matrix_package': [['location_matrix', 'project_id']],
        'media': [
            ['assethandoverdocumentmedia_set', 'asset_handover_document', 'asset_handover', 'project_id'],
            ['locationmatrixpackage_set', 'location_matrix_package', 'location_matrix', 'project_id'],
            ['packagehandoverdocumentmedia_set', 'package_handover_document', 'project_id'],
            ['qualityissue_set', 'location_matrix', 'project_id'],
            ['qualityissueupdate_set', 'quality_issue', 'location_matrix', 'project_id'],
            ['subtask_set', 'task', 'project_id'],
            ['subtaskupdate_set', 'subtask', 'task', 'project_id'],
            ['taskupdate_set', 'task', 'project_id'],
        ],
        'package_matrix': [['project_id']],
        'package_matrix_hidden_activity_task': [['package_matrix', 'project_id']],
        'project': [['pk']],
        'project_news': [['project_id']],
        'project_user': [['project_id']],
        'quality_issue_update': [['quality_issue', 'location_matrix', 'project_id']],
        'quality_issue': [['location_matrix', 'project_id']],
        'response_category': [['project_id']],
        'subtask': [['task', 'location_matrix', 'project_id']],
        'subtask_update': [['subtask', 'task', 'location_matrix', 'project_id']],
        'task': [['location_matrix', 'project_id']],
        'task_update': [['task', 'location_matrix', 'project_id']],
    }

    return field_map.get(instance.get_snake_case_class_name())


def model_serialization_map(instance):
    snake_case_model_class_name = instance.get_snake_case_class_name()
    field_map = {
        'location_matrix': {
            'serializer': LocationMatrixSerializer,
            'expand': []
        },
        'location_matrix_package': {
            'serializer': LocationMatrixPackagesSerializer,
            'expand': []
        },
        'media': {
            'serializer': MediaSerializer,
            'expand': [
                'expanded_project_snapshot_thumbnails.expanded_thumbnail',
                'expanded_project_snapshot_thumbnails.expanded_original_media',
                'expanded_thumbnails.expanded_thumbnail',
                'expanded_thumbnails.expanded_original_media'
            ]
        },
        'media_thumbnail': {
            'serializer': MediaThumbnailSerializer,
            'expand': ['expanded_thumbnail', 'expanded_original_media']
        },
        'package': {
            'serializer': PackageSerializer,
            'expand': []
        },
        'package_activity': {
            'serializer': PackageActivitySerializer,
            'expand': []
        },
        'package_activity_task': {
            'serializer': PackageActivityTaskSerializer,
            'expand': []
        },
        'package_matrix': {
            'serializer': PackageMatrixSerializer,
            'expand': ['expanded_package', 'expanded_package_activity', 'expanded_project']
        },
        'package_matrix_hidden_activity_task': {
            'serializer': PackageMatrixHiddenActivityTaskSerializer,
            'expand': ['package_matrix.package', 'package_matrix.package_activity', 'package_matrix.project']
        },
        'project': {
            'serializer': ProjectSerializer,
            'expand': ['expanded_key_contacts']
        },
        'project_user': {
            'serializer': ProjectUserSerializer,
            'expand': ['expanded_user']
        },
        'project_news': {
            'serializer': ProjectNewsSerializer,
            'expand': []
        },
        'quality_issue': {
            'serializer': QualityIssueSerializer,
            'expand': []
        },
        'quality_issue_update': {
            'serializer': QualityIssueUpdateSerializer,
            'expand': []
        },
        'recipient': {
            'serializer': RecipientSerializer,
            'expand': ['expanded_user']
        },
        'response_category': {
            'serializer': ResponseCategorySerializer,
            'expand': ['expanded_project']
        },
        'subtask': {
            'serializer': SubtaskSerializer,
            'expand': []
        },
        'subtask_update': {
            'serializer': SubtaskUpdateSerializer,
            'expand': []
        },
        'task': {
            'serializer': TaskSerializer,
            'expand': []
        },
        'task_update': {
            'serializer': TaskUpdateSerializer,
            'expand': []
        },
        'user': {
            'serializer': UserSerializer,
            'expand': []
        },
        'company': {
            'serializer': CompanySerializer,
            'expand': []
        },
        'package_matrix_company': {
            'serializer': PackageMatrixCompanySerializer,
            'expand': ['expanded_package_matrix.expanded_package', 'expanded_package_matrix.expanded_package_activity', 'expanded_package_matrix.expanded_project', 'expanded_company']
        }
    }

    return field_map.get(snake_case_model_class_name)


def get_project_id(instance):
    field_paths = project_field_path(instance)

    if field_paths is None:
        return None

    current_field = instance

    for field_path in field_paths:
        for field in field_path:
            try:
                local_field = getattr(current_field, field)
                if isinstance(local_field, BaseManager):
                    local_field = local_field.first()

                if local_field is None:
                    break

                current_field = local_field

            except ObjectDoesNotExist as e:
                return None

    return None if current_field == instance else current_field
