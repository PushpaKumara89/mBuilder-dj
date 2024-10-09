from django.dispatch import receiver

from api.signals.models.signal import post_update
from api.utilities.event_utilities import create_events_for_post_update


@receiver(post_update)
def on_post_update(sender, **kwargs):
    if sender.create_events_on_update and kwargs.get('instances'):
        kwargs['instances'] = list(sender.all_objects.filter(pk__in=kwargs.get('instances')).all())

        create_events_for_post_update(**kwargs)
