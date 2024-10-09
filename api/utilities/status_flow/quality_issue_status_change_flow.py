from api.models import User, QualityIssue
from api.utilities.status_flow.base_status_flow import BaseStatusFlow
from api.utilities.status_flow.transition import TransitionPack
from api.utilities.status_flow.transition import Transition


class QualityIssueStatusChangeFlow(BaseStatusFlow):
    MULTIPLEX_SYNCED_REJECT = TransitionPack([
        Transition(from_status=QualityIssue.Status.UNDER_INSPECTION, to_status=QualityIssue.Status.INSPECTION_REJECTED),
    ])

    MULTIPLEX_SYNCED_REMOVE = TransitionPack([
        Transition(from_status=QualityIssue.Status.CONTESTED, to_status=QualityIssue.Status.REMOVED)
    ])

    MULTIPLEX_SYNCED_RE_OPEN = TransitionPack([
        Transition(from_status=QualityIssue.Status.REMOVED, to_status=QualityIssue.Status.IN_PROGRESS),
        Transition(from_status=QualityIssue.Status.CLOSED, to_status=QualityIssue.Status.IN_PROGRESS),
        Transition(from_status=QualityIssue.Status.CONTESTED, to_status=QualityIssue.Status.IN_PROGRESS),
        Transition(from_status=QualityIssue.Status.REQUESTING_APPROVAL, to_status=QualityIssue.Status.IN_PROGRESS),
        Transition(from_status=QualityIssue.Status.DECLINED, to_status=QualityIssue.Status.IN_PROGRESS),
        Transition(from_status=QualityIssue.Status.REQUESTED_APPROVAL_REJECTED, to_status=QualityIssue.Status.IN_PROGRESS)
    ])

    SUBCONTRACTOR_SYNCED_CLOSE_OUT = TransitionPack([
        Transition(from_status=QualityIssue.Status.IN_PROGRESS, to_status=QualityIssue.Status.UNDER_INSPECTION),
        Transition(from_status=QualityIssue.Status.INSPECTION_REJECTED, to_status=QualityIssue.Status.UNDER_INSPECTION),
    ])

    SUBCONTRACTOR_SYNCED_DECLINE = TransitionPack([
        Transition(from_status=QualityIssue.Status.IN_PROGRESS, to_status=QualityIssue.Status.DECLINED),
        Transition(from_status=QualityIssue.Status.INSPECTION_REJECTED, to_status=QualityIssue.Status.DECLINED)
    ])

    SUBCONTRACTOR_SYNCED_REJECT = TransitionPack([
        Transition(from_status=QualityIssue.Status.INSPECTION_REJECTED, to_status=QualityIssue.Status.CONTESTED),
    ])
    
    CLIENTS_REMOVE = TransitionPack([
        Transition(from_status=QualityIssue.Status.CONTESTED, to_status=QualityIssue.Status.REMOVED),
        Transition(from_status=QualityIssue.Status.UNDER_REVIEW, to_status=QualityIssue.Status.REMOVED),
    ])

    CLIENTS_REJECT = TransitionPack([
        Transition(from_status=QualityIssue.Status.REQUESTING_APPROVAL, to_status=QualityIssue.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    CLIENTS_EDIT = TransitionPack([
        Transition(from_status=QualityIssue.Status.CONTESTED, to_status=QualityIssue.Status.UNDER_REVIEW)
    ])

    CLIENTS_CLOSE_OUT = TransitionPack([
        Transition(from_status=QualityIssue.Status.REQUESTING_APPROVAL, to_status=QualityIssue.Status.CLOSED)
    ])

    CLIENTS_UNDO = TransitionPack([
        Transition(from_status=QualityIssue.Status.CLOSED, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.REQUESTED_APPROVAL_REJECTED, to_status=QualityIssue.Status.REQUESTING_APPROVAL)
    ])

    MULTIPLEX_OPEN = TransitionPack([
        Transition(from_status=QualityIssue.Status.UNDER_REVIEW, to_status=QualityIssue.Status.IN_PROGRESS)
    ])

    MULTIPLEX_CONTEST = TransitionPack([
        Transition(from_status=QualityIssue.Status.UNDER_REVIEW, to_status=QualityIssue.Status.CONTESTED),
        Transition(from_status=QualityIssue.Status.DECLINED, to_status=QualityIssue.Status.CONTESTED)
    ])

    MULTIPLEX_REJECT = TransitionPack([
        Transition(from_status=QualityIssue.Status.REQUESTED_APPROVAL_REJECTED, to_status=QualityIssue.Status.REQUESTING_APPROVAL)
    ])

    MULTIPLEX_UNDO = TransitionPack([
        Transition(from_status=QualityIssue.Status.CONTESTED, to_status=QualityIssue.Status.UNDER_REVIEW),
        Transition(from_status=QualityIssue.Status.REQUESTING_APPROVAL, to_status=QualityIssue.Status.IN_PROGRESS),
        Transition(from_status=QualityIssue.Status.CONTESTED, to_status=QualityIssue.Status.DECLINED),
    ])

    MULTIPLEX_REQUEST_APPROVAL = TransitionPack([
        Transition(from_status=QualityIssue.Status.IN_PROGRESS, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.UNDER_INSPECTION, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.REMOVED, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.CONTESTED, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.INSPECTION_REJECTED, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.REQUESTED_APPROVAL_REJECTED, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.CLOSED, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.UNDER_REVIEW, to_status=QualityIssue.Status.REQUESTING_APPROVAL),
        Transition(from_status=QualityIssue.Status.DECLINED, to_status=QualityIssue.Status.REQUESTING_APPROVAL)
    ])

    MULTIPLEX_CLOSE_OUT = TransitionPack([
        Transition(from_status=QualityIssue.Status.REQUESTING_APPROVAL, to_status=QualityIssue.Status.CLOSED),
        Transition(from_status=QualityIssue.Status.CONTESTED, to_status=QualityIssue.Status.CLOSED),
        Transition(from_status=QualityIssue.Status.INSPECTION_REJECTED, to_status=QualityIssue.Status.CLOSED),
        Transition(from_status=QualityIssue.Status.IN_PROGRESS, to_status=QualityIssue.Status.CLOSED),
        Transition(from_status=QualityIssue.Status.REMOVED, to_status=QualityIssue.Status.CLOSED),
        Transition(from_status=QualityIssue.Status.UNDER_REVIEW, to_status=QualityIssue.Status.CLOSED),
        Transition(from_status=QualityIssue.Status.UNDER_INSPECTION, to_status=QualityIssue.Status.CLOSED),
        Transition(from_status=QualityIssue.Status.REQUESTED_APPROVAL_REJECTED, to_status=QualityIssue.Status.CLOSED),
    ])

    CLIENTS_ALLOWED_ACTIONS = CLIENTS_REMOVE + CLIENTS_EDIT + CLIENTS_CLOSE_OUT + CLIENTS_REJECT + CLIENTS_UNDO

    CLIENTS_CONFIRMED_ACTIONS = CLIENTS_REMOVE + CLIENTS_EDIT + CLIENTS_CLOSE_OUT + CLIENTS_REJECT

    MULTIPLEX_ALLOWED_ACTIONS = MULTIPLEX_OPEN + MULTIPLEX_CONTEST + MULTIPLEX_REJECT + MULTIPLEX_CLOSE_OUT + \
                                MULTIPLEX_UNDO + MULTIPLEX_REQUEST_APPROVAL

    MULTIPLEX_CONFIRMED_ACTIONS = MULTIPLEX_OPEN + MULTIPLEX_CONTEST + MULTIPLEX_REJECT + MULTIPLEX_REQUEST_APPROVAL \
                                  + MULTIPLEX_SYNCED_REJECT + MULTIPLEX_SYNCED_REMOVE + MULTIPLEX_SYNCED_RE_OPEN

    SUBCONTRACTOR_CONFIRMED_ACTIONS = SUBCONTRACTOR_SYNCED_CLOSE_OUT + SUBCONTRACTOR_SYNCED_DECLINE + \
                                      SUBCONTRACTOR_SYNCED_REJECT
    STATUS_TRANSITIONS = {
        User.Group.CLIENT.value: CLIENTS_ALLOWED_ACTIONS,
        User.Group.CONSULTANT.value: CLIENTS_ALLOWED_ACTIONS,
        User.Group.MANAGER.value: MULTIPLEX_ALLOWED_ACTIONS,
        User.Group.ADMIN.value: MULTIPLEX_ALLOWED_ACTIONS,
        User.Group.COMPANY_ADMIN.value: MULTIPLEX_ALLOWED_ACTIONS
    }

    CONFIRMED_UPDATE_TRANSITIONS = {
        User.Group.CLIENT.value: CLIENTS_CONFIRMED_ACTIONS,
        User.Group.CONSULTANT.value: CLIENTS_CONFIRMED_ACTIONS,
        User.Group.MANAGER.value: MULTIPLEX_CONFIRMED_ACTIONS,
        User.Group.ADMIN.value: MULTIPLEX_CONFIRMED_ACTIONS,
        User.Group.COMPANY_ADMIN.value: MULTIPLEX_CONFIRMED_ACTIONS,
        User.Group.SUBCONTRACTOR.value: SUBCONTRACTOR_CONFIRMED_ACTIONS
    }

    def is_valid_change(self):
        if self.user.is_superuser:
            return True

        if not self.transition.from_status:
            return (self.user.is_client or self.user.is_consultant) and \
                   self.transition.to_status == QualityIssue.Status.UNDER_REVIEW

        if self.transition.from_status == self.transition.to_status:
            return True

        status_transitions = self.STATUS_TRANSITIONS.get(self.user.group.pk, [])

        return self.transition in status_transitions

    def is_remove(self):
        return self.transition in self.CLIENTS_REMOVE

    def is_multiplex_requesting_approval(self):
        return self.transition in self.MULTIPLEX_REQUEST_APPROVAL

    def is_contest(self):
        return self.transition in self.MULTIPLEX_CONTEST

    def is_requested_approval_rejected_update(self):
        return self.is_update() and self.transition.from_status == QualityIssue.Status.REQUESTED_APPROVAL_REJECTED

    def is_requested_approval_rejected(self):
        return self.transition in self.CLIENTS_REJECT

    def get_confirmed_transitions(self):
        return self.CLIENTS_CONFIRMED_ACTIONS + self.MULTIPLEX_CONFIRMED_ACTIONS
