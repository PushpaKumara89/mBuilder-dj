from django.db.models.signals import post_delete
from django.dispatch import receiver
from safedelete.signals import post_softdelete

from api.models import Project
from api.queues.asset_handover_statistics import delete_statistics_on_project_delete


@receiver((post_delete, post_softdelete), sender=Project)
def on_project_delete(sender, instance: Project, **kwargs):
    if not kwargs.get('raw', False):
        delete_statistics_on_project_delete(instance)
