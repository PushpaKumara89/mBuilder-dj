from django.dispatch import receiver

from api.signals.models import post_bulk_create
from api.utilities.event_utilities import create_events_for_bulk_post_save, get_project_id


@receiver(post_bulk_create)
def on_post_bulk_create(sender, **kwargs):
    instances = kwargs.get('instances', [])
    instances = instances if type(instances) in [list, frozenset, set] else []

    if len(instances) == 0 or not sender.create_events_on_update:
        return

    kwargs['project_id'] = get_project_id(instances[0])

    create_events_for_bulk_post_save(**kwargs)
