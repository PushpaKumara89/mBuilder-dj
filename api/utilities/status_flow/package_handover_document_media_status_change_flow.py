from api.models import User, PackageHandoverDocumentMedia
from api.utilities.status_flow.base_status_flow import BaseStatusFlow
from api.utilities.status_flow.transition import TransitionPack
from api.utilities.status_flow.transition import Transition


class PackageHandoverDocumentMediaStatusChangeFlow(BaseStatusFlow):

    UPLOAD = TransitionPack([
        Transition(from_status=None,
                   to_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS)
    ])

    UPLOAD_BY_MULTIPLEX = TransitionPack([
        Transition(from_status=None,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL)
    ])

    REUPLOAD = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.CONTESTED, to_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS)
    ])

    CONTEST = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS, to_status=PackageHandoverDocumentMedia.Status.CONTESTED)
    ])

    UNDO_CONTEST = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.CONTESTED,
                   to_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS)
    ])

    REQUESTING_APPROVAL = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL)
    ])

    UNDO_REQUESTING_APPROVAL = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS)
    ])

    ACCEPT = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=PackageHandoverDocumentMedia.Status.ACCEPTED)
    ])

    REJECT_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    UNDO_REJECT_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL)
    ])

    ACCEPT_REJECTING_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=PackageHandoverDocumentMedia.Status.CONTESTED)
    ])

    UNDO_ACCEPT_REJECTING_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.CONTESTED,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    DECLINE_REJECTING_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL)
    ])

    UNDO_DECLINE_REJECTING_APPROVAL_REQUEST = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    REMOVE_SUBCONTRACTOR_AND_CONSULTANT = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=PackageHandoverDocumentMedia.Status.CONTESTED,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED)
    ])

    REMOVE_BY_STAFF = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=PackageHandoverDocumentMedia.Status.CONTESTED,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
    ])

    REMOVE_BY_COMPANY_ADMIN = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.ACCEPTED,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
    ])

    MULTIPLEX_BULK_UPDATE = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL),
        Transition(from_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=PackageHandoverDocumentMedia.Status.CONTESTED),
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL),
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                   to_status=PackageHandoverDocumentMedia.Status.CONTESTED),
    ])

    COMPANY_ADMIN_BULK_UPDATE = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.ACCEPTED,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
    ])

    CLIENT_BULK_UPDATE = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=PackageHandoverDocumentMedia.Status.ACCEPTED),
        Transition(from_status=PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                   to_status=PackageHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED),
    ])

    CONSULTANT_BULK_UPDATE = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=PackageHandoverDocumentMedia.Status.CONTESTED,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
    ])

    SUBCONTRACTOR_BULK_UPDATE = TransitionPack([
        Transition(from_status=PackageHandoverDocumentMedia.Status.IN_PROGRESS,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
        Transition(from_status=PackageHandoverDocumentMedia.Status.CONTESTED,
                   to_status=PackageHandoverDocumentMedia.Status.REMOVED),
    ])

    CONFIRMED_MULTIPLEX_TRANSITIONS = UPLOAD_BY_MULTIPLEX + CONTEST + REQUESTING_APPROVAL + ACCEPT_REJECTING_APPROVAL_REQUEST + DECLINE_REJECTING_APPROVAL_REQUEST

    UNDO_MULTIPLEX_TRANSITIONS = UNDO_CONTEST + UNDO_REQUESTING_APPROVAL + UNDO_ACCEPT_REJECTING_APPROVAL_REQUEST + UNDO_DECLINE_REJECTING_APPROVAL_REQUEST

    CONFIRMED_CLIENT_TRANSITIONS = ACCEPT + REJECT_APPROVAL_REQUEST

    UNDO_CLIENT_TRANSITIONS = UNDO_REJECT_APPROVAL_REQUEST

    STATUS_TRANSITIONS = {
        User.Group.SUBCONTRACTOR.value: UPLOAD + REUPLOAD + REMOVE_SUBCONTRACTOR_AND_CONSULTANT,
        User.Group.CONSULTANT.value: UPLOAD + REUPLOAD + REMOVE_SUBCONTRACTOR_AND_CONSULTANT,
        User.Group.MANAGER.value: CONFIRMED_MULTIPLEX_TRANSITIONS + UNDO_MULTIPLEX_TRANSITIONS + REMOVE_BY_STAFF,
        User.Group.ADMIN.value: CONFIRMED_MULTIPLEX_TRANSITIONS + UNDO_MULTIPLEX_TRANSITIONS + REMOVE_BY_STAFF,
        User.Group.COMPANY_ADMIN.value: CONFIRMED_MULTIPLEX_TRANSITIONS + UNDO_MULTIPLEX_TRANSITIONS + REMOVE_BY_COMPANY_ADMIN + REMOVE_BY_STAFF,
        User.Group.CLIENT.value: CONFIRMED_CLIENT_TRANSITIONS + UNDO_CLIENT_TRANSITIONS
    }

    CONFIRMED_UPDATE_TRANSITIONS = {
        User.Group.SUBCONTRACTOR.value: UPLOAD + REUPLOAD + REMOVE_SUBCONTRACTOR_AND_CONSULTANT,
        User.Group.CONSULTANT.value: UPLOAD + REUPLOAD + REMOVE_SUBCONTRACTOR_AND_CONSULTANT,
        User.Group.MANAGER.value: CONFIRMED_MULTIPLEX_TRANSITIONS + REMOVE_BY_STAFF,
        User.Group.ADMIN.value: CONFIRMED_MULTIPLEX_TRANSITIONS + REMOVE_BY_STAFF,
        User.Group.COMPANY_ADMIN.value: CONFIRMED_MULTIPLEX_TRANSITIONS + REMOVE_BY_COMPANY_ADMIN + REMOVE_BY_STAFF,
        User.Group.CLIENT.value: CONFIRMED_CLIENT_TRANSITIONS
    }

    BULK_UPDATE_TRANSITIONS = {
        User.Group.COMPANY_ADMIN.value: MULTIPLEX_BULK_UPDATE + COMPANY_ADMIN_BULK_UPDATE,
        User.Group.ADMIN.value: MULTIPLEX_BULK_UPDATE,
        User.Group.MANAGER.value: MULTIPLEX_BULK_UPDATE,
        User.Group.CLIENT.value: CLIENT_BULK_UPDATE,
        User.Group.CONSULTANT.value: CONSULTANT_BULK_UPDATE,
        User.Group.SUBCONTRACTOR.value: SUBCONTRACTOR_BULK_UPDATE,
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

    def get_confirmed_transitions(self):
        return self.UPLOAD + self.REUPLOAD + self.CONFIRMED_MULTIPLEX_TRANSITIONS + self.CONFIRMED_CLIENT_TRANSITIONS

    def is_valid_bulk_update(self):
        status_transitions = self.BULK_UPDATE_TRANSITIONS.get(self.user.group.pk, [])

        if self.transition.from_status == self.transition.to_status:
            return False

        return self.transition in status_transitions
