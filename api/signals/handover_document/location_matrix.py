from typing import List

from django.dispatch import receiver

from api.models import LocationMatrix
from api.queues.handover_document import update_handover_document_on_location_matrix_update
from api.signals.models.signal import post_bulk_update


@receiver(signal=post_bulk_update, sender=LocationMatrix)
def on_location_matrix_update(sender, instances: List[LocationMatrix], **kwargs):
    update_handover_document_on_location_matrix_update(instances)
