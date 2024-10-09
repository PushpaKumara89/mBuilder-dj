from typing import Union

import pendulum
from django.db.models import Q, CharField
from django.db.models.expressions import RawSQL, Value
from django.db.models.functions import Concat
from django.forms.models import model_to_dict

from api.models import QualityIssue, Subtask, QualityIssueUpdate, SubtaskUpdate, PackageHandoverDocumentMediaUpdate, \
    PackageHandoverDocumentMedia, AssetHandoverDocumentMediaUpdate, AssetHandoverDocumentMedia
from api.utilities.status_flow.asset_handover_document_media_status_change_flow import AssetHandoverDocumentMediaStatusChangeFlow
from api.utilities.status_flow.base_status_flow import BaseStatusFlow
from api.utilities.status_flow.quality_issue_status_change_flow import QualityIssueStatusChangeFlow
from api.utilities.status_flow.subtask_status_change_flow import SubtaskStatusChangeFlow
from api.utilities.status_flow.package_handover_document_media_status_change_flow import \
    PackageHandoverDocumentMediaStatusChangeFlow


def set_last_confirmed_update(entity_update: Union[QualityIssueUpdate, SubtaskUpdate, AssetHandoverDocumentMediaUpdate,
                                                   PackageHandoverDocumentMediaUpdate], user):
    def does_it_confirmation_update_edit():
        last_update_with_changed_status = get_last_update_with_changed_status(entity)

        if not last_update_with_changed_status:
            return False

        entity_status_change_flow = status_flow_class(model_to_dict(last_update_with_changed_status), user)

        # For confirmation edit we need to check that in current request
        # we don't update entity itself, only confirmation update.
        # Condition len(entity_status_flow.new_data) helps us to detect that update payload
        # contains only the status field.
        return entity_status_flow.is_update() and len(entity_status_flow.new_data) == 1 \
            and entity_status_change_flow.is_confirmed_update()

    status_flow_class = get_status_flow_class(entity_update)
    entity_status_flow = status_flow_class(model_to_dict(entity_update), user)
    entity = get_updated_entity(entity_update)

    if entity_status_flow.is_confirmed_update() or does_it_confirmation_update_edit():
        assign_last_confirmed_update(entity, entity_update)
    elif entity_status_flow.is_undo() and bool(entity.last_confirmed_update):
        current_last_confirmed_update = entity.last_confirmed_update
        if current_last_confirmed_update.new_data['status'] == current_last_confirmed_update.old_data.get('status'):
            update_with_changed_status = get_last_update_with_changed_status(entity)

            if not update_with_changed_status:
                previous_confirmed_transition = None
            else:
                previous_confirmed_transition = get_previously_confirmed_transition(
                    entity, entity_status_flow, update_with_changed_status
                )
        else:
            previous_confirmed_transition = get_previously_confirmed_transition(
                entity, entity_status_flow, current_last_confirmed_update
            )

        if previous_confirmed_transition is None or previous_confirmed_transition.id == current_last_confirmed_update.id:
            return

        assign_last_confirmed_update(entity, previous_confirmed_transition)


def get_previously_confirmed_transition(entity: Union[QualityIssue, Subtask, PackageHandoverDocumentMedia,
                                                      AssetHandoverDocumentMedia],
                                        entity_status_flow: BaseStatusFlow,
                                        last_confirmed_update: Union[QualityIssueUpdate, SubtaskUpdate,
                                                                     PackageHandoverDocumentMediaUpdate,
                                                                     AssetHandoverDocumentMediaUpdate]):
    update_set = get_update_entity_set(entity)

    return update_set. \
        annotate(transition=Concat(RawSQL('old_data ->> %s ', ('status',)),
                                   Value('-'),
                                   RawSQL('new_data ->> %s', ('status',)),
                                   output_field=CharField())). \
        filter(~Q(pk=last_confirmed_update.pk),
               Q(Q(transition__in=list(entity_status_flow.get_confirmed_transitions_filtered_by_to_status())) |
                 Q(transition=f'{entity_status_flow.transition.to_status}-{entity_status_flow.transition.to_status}')),
               created_at__lt=last_confirmed_update.created_at). \
        order_by('-created_at').first()


def assign_last_confirmed_update(entity: Union[QualityIssue, Subtask, PackageHandoverDocumentMedia,
                                               AssetHandoverDocumentMedia],
                                 last_confirmed_update: Union[QualityIssueUpdate, SubtaskUpdate,
                                                              PackageHandoverDocumentMediaUpdate,
                                                              AssetHandoverDocumentMediaUpdate]):
    setattr(entity, 'last_confirmed_update_id', last_confirmed_update.id)
    setattr(entity, 'updated_at', pendulum.now())

    entity.save(update_fields=['last_confirmed_update_id', 'updated_at'])


def get_last_update_with_changed_status(entity: Union[QualityIssue, Subtask, PackageHandoverDocumentMedia,
                                                      AssetHandoverDocumentMedia]):
    if hasattr(entity, 'last_updates_with_changed_status'):
        return entity.last_updates_with_changed_status[0] if entity.last_updates_with_changed_status else None

    update_set = get_update_entity_set(entity)

    if isinstance(entity, (QualityIssueUpdate, SubtaskUpdate)):
        return update_set.all().get_with_changed_status_in_desc_order().first()

    return update_set.filter(~Q(
        old_data__status=RawSQL('new_data -> %s', ('status',))
    )).order_by('-created_at').first()


def get_status_flow_class(entity_update: Union[QualityIssueUpdate, SubtaskUpdate, PackageHandoverDocumentMediaUpdate]):
    if isinstance(entity_update, QualityIssueUpdate):
        return QualityIssueStatusChangeFlow
    elif isinstance(entity_update, SubtaskUpdate):
        return SubtaskStatusChangeFlow
    elif isinstance(entity_update, PackageHandoverDocumentMediaUpdate):
        return PackageHandoverDocumentMediaStatusChangeFlow
    elif isinstance(entity_update, AssetHandoverDocumentMediaUpdate):
        return AssetHandoverDocumentMediaStatusChangeFlow


def get_updated_entity(entity_update: Union[QualityIssueUpdate, SubtaskUpdate, PackageHandoverDocumentMediaUpdate,
                                            AssetHandoverDocumentMediaUpdate]):
    if isinstance(entity_update, QualityIssueUpdate):
        return entity_update.quality_issue
    elif isinstance(entity_update, SubtaskUpdate):
        return entity_update.subtask
    elif isinstance(entity_update, PackageHandoverDocumentMediaUpdate):
        return entity_update.package_handover_document_media
    elif isinstance(entity_update, AssetHandoverDocumentMediaUpdate):
        return entity_update.asset_handover_document_media


def get_update_entity_set(entity: Union[QualityIssue, Subtask, PackageHandoverDocumentMedia,
                                        AssetHandoverDocumentMedia]):
    if isinstance(entity, QualityIssue):
        return entity.qualityissueupdate_set
    elif isinstance(entity, Subtask):
        return entity.subtaskupdate_set
    elif isinstance(entity, PackageHandoverDocumentMedia):
        return entity.packagehandoverdocumentmediaupdate_set
    elif isinstance(entity, AssetHandoverDocumentMedia):
        return entity.assethandoverdocumentmediaupdate_set
