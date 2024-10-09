from api.models import User, AssetHandoverDocumentMedia
from api.utilities.status_flow.base_status_flow import BaseStatusFlow
from api.utilities.status_flow.transition import TransitionPack
from api.utilities.status_flow.transition import Transition


class AssetHandoverDocumentMediaStatusChangeFlow(BaseStatusFlow):

    UPLOAD = TransitionPack([
        Transition(from_status=None,
                   to_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS)
    ])

    UPLOAD_BY_MULTIPLEX = TransitionPack([
        Transition(from_status=None,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL)
    ])

    REUPLOAD = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.CONTESTED,
                   to_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS)
    ])

    CONTEST = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=AssetHandoverDocumentMedia.Status.CONTESTED)
    ])

    UNDO_CONTEST = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.CONTESTED,
                   to_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS)
    ])

    REQUESTING_APPROVAL = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL)
    ])

    UNDO_REQUESTING_APPROVAL = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS)
    ])

    ACCEPT = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=AssetHandoverDocumentMedia.Status.ACCEPTED)
    ])

    REJECT_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    UNDO_REJECT_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL)
    ])

    ACCEPT_REJECTING_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=AssetHandoverDocumentMedia.Status.CONTESTED)
    ])

    UNDO_ACCEPT_REJECTING_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.CONTESTED,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    DECLINE_REJECTING_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL)
    ])

    UNDO_DECLINE_REJECTING_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    REMOVE_SUBCONTRACTOR = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=AssetHandoverDocumentMedia.Status.CONTESTED,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED)
    ])

    REMOVE_BY_MULTIPLEX = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=AssetHandoverDocumentMedia.Status.CONTESTED,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=AssetHandoverDocumentMedia.Status.ACCEPTED,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED),
    ])

    BULK_UPDATE_BY_COMPANY_ADMIN = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.ACCEPTED,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED)
    ])

    BULK_UPDATE_BY_MULTIPLEX = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL),
        Transition(from_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=AssetHandoverDocumentMedia.Status.CONTESTED),
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL),
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=AssetHandoverDocumentMedia.Status.CONTESTED),
    ])

    BULK_UPDATE_BY_CLIENT = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=AssetHandoverDocumentMedia.Status.ACCEPTED),
        Transition(from_status=AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED),
    ])

    BULK_UPDATE_BY_SUBCONTRACTOR = TransitionPack([
        Transition(from_status=AssetHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=AssetHandoverDocumentMedia.Status.CONTESTED,
                   to_status=AssetHandoverDocumentMedia.Status.REMOVED),
    ])

    CONFIRMED_MULTIPLEX_TRANSITIONS = UPLOAD_BY_MULTIPLEX + CONTEST + REQUESTING_APPROVAL + ACCEPT_REJECTING_APPROVAL_REQUEST + DECLINE_REJECTING_APPROVAL_REQUEST

    UNDO_MULTIPLEX_TRANSITIONS = UNDO_CONTEST + UNDO_REQUESTING_APPROVAL + UNDO_ACCEPT_REJECTING_APPROVAL_REQUEST + UNDO_DECLINE_REJECTING_APPROVAL_REQUEST

    CONFIRMED_CLIENT_TRANSITIONS = ACCEPT + REJECT_APPROVAL_REQUEST

    UNDO_CLIENT_TRANSITIONS = UNDO_REJECT_APPROVAL_REQUEST

    STATUS_TRANSITIONS = {
        User.Group.SUBCONTRACTOR.value: UPLOAD + REUPLOAD + REMOVE_SUBCONTRACTOR,
        User.Group.MANAGER.value: CONFIRMED_MULTIPLEX_TRANSITIONS + UNDO_MULTIPLEX_TRANSITIONS + REMOVE_BY_MULTIPLEX,
        User.Group.ADMIN.value: CONFIRMED_MULTIPLEX_TRANSITIONS + UNDO_MULTIPLEX_TRANSITIONS + REMOVE_BY_MULTIPLEX,
        User.Group.COMPANY_ADMIN.value: CONFIRMED_MULTIPLEX_TRANSITIONS + UNDO_MULTIPLEX_TRANSITIONS + REMOVE_BY_MULTIPLEX,
        User.Group.CLIENT.value: CONFIRMED_CLIENT_TRANSITIONS + UNDO_CLIENT_TRANSITIONS
    }

    CONFIRMED_UPDATE_TRANSITIONS = {
        User.Group.SUBCONTRACTOR.value: UPLOAD + REUPLOAD + REMOVE_SUBCONTRACTOR,
        User.Group.MANAGER.value: CONFIRMED_MULTIPLEX_TRANSITIONS + REMOVE_BY_MULTIPLEX,
        User.Group.ADMIN.value: CONFIRMED_MULTIPLEX_TRANSITIONS + REMOVE_BY_MULTIPLEX,
        User.Group.COMPANY_ADMIN.value: CONFIRMED_MULTIPLEX_TRANSITIONS + REMOVE_BY_MULTIPLEX,
        User.Group.CLIENT.value: CONFIRMED_CLIENT_TRANSITIONS
    }

    BULK_UPDATE_TRANSITIONS = {
        User.Group.COMPANY_ADMIN.value: BULK_UPDATE_BY_COMPANY_ADMIN + BULK_UPDATE_BY_MULTIPLEX,
        User.Group.ADMIN.value: BULK_UPDATE_BY_MULTIPLEX,
        User.Group.MANAGER.value: BULK_UPDATE_BY_MULTIPLEX,
        User.Group.CLIENT.value: BULK_UPDATE_BY_CLIENT,
        User.Group.SUBCONTRACTOR.value: BULK_UPDATE_BY_SUBCONTRACTOR,
    }

    def is_confirmed_update(self):
        confirmed_updates = self.CONFIRMED_UPDATE_TRANSITIONS.get(self.user.group.pk, [])
        return 'status' in self.new_data and self.transition in confirmed_updates

    def is_valid_change(self):
        # Add validation for old_data.status = entity.status
        if self.user.is_superuser:
            return True

        status_transitions = self.STATUS_TRANSITIONS.get(self.user.group.pk, [])

        if self.transition.from_status == self.transition.to_status:
            return True

        return self.transition in status_transitions

    def is_valid_bulk_update(self):
        status_transitions = self.STATUS_TRANSITIONS.get(self.user.group.pk, [])

        if self.transition.from_status == self.transition.to_status:
            return False

        return self.transition in status_transitions

    def get_confirmed_transitions(self):
        return self.UPLOAD + self.REUPLOAD + self.CONFIRMED_MULTIPLEX_TRANSITIONS + self.CONFIRMED_CLIENT_TRANSITIONS
