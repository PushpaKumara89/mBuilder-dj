from api.enums.entities import Entities
from api.models import User
from api.utilities.event_utilities import perform_event_creation, create_events_for_project_m2m_reverse_post_delete, \
    model_serialization_map


def create_m2m_event(**kwargs):
    child_queryset = getattr(kwargs.get('instance'), kwargs.get('relation'))
    pk_set = set(child_queryset.values_list('pk', flat=True))
    data = {
        'instance': kwargs.get('instance'),
        'pk_set': pk_set,
        'action': kwargs.get('action'),
        'model': kwargs['model']
    }

    perform_event_creation(kwargs.get('parent_entity_field'), kwargs.get('child_entity_field'),
                           kwargs.get('event_entity_name'), data)


def create_key_contacts_m2m_reverse_deletion_events(instance: User):
    projects = list(instance.key_contacts.all())
    mapping = model_serialization_map(instance)
    user = mapping['serializer'](instance, expand=mapping['expand']).data

    entities = [{'project': project.pk, 'user': user} for project in projects]

    entity_name = Entities.PROJECT_KEY_CONTACTS.value

    create_events_for_project_m2m_reverse_post_delete(entities, entity_name)


def create_reverse_m2m_event(**kwargs):
    pk_set = [kwargs.get('child_instance').pk]
    parent_instances = kwargs.get('parent_instances')

    for parent_instance in parent_instances:
        data = {
            'instance': parent_instance,
            'pk_set': pk_set,
            'action': kwargs.get('action'),
            'model': kwargs['model']
        }

        perform_event_creation(kwargs.get('parent_entity_field'), kwargs.get('child_entity_field'),
                               kwargs.get('event_entity_name'), data)
