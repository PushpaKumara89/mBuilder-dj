from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import SubtaskUpdate

@receiver(post_save, sender=SubtaskUpdate)
def subtask_update_post_save(sender, instance: SubtaskUpdate, **kwargs):
    if kwargs.get('created', False) and not kwargs.get('raw', False):
        instance.subtask.last_update = instance
        instance.subtask.save(update_fields=['last_update'])