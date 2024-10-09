from api.models import User, Subtask
from api.models.base_model import BaseModel
from api.utilities.status_flow.base_status_flow import BaseStatusFlow
from api.utilities.status_flow.transition import TransitionPack
from api.utilities.status_flow.transition import Transition


class SubtaskStatusChangeFlow(BaseStatusFlow):
    CLIENTS_SYNCED_REMOVE = TransitionPack([
        Transition(from_status=Subtask.Status.CONTESTED, to_status=Subtask.Status.REMOVED),
    ])

    CLIENTS_SYNCED_CLOSE_OUT = TransitionPack([
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.CLOSED)
    ])

    MULTIPLEX_REJECT = TransitionPack([
        Transition(from_status=Subtask.Status.UNDER_INSPECTION, to_status=Subtask.Status.INSPECTION_REJECTED),
        Transition(from_status=Subtask.Status.REQUESTED_APPROVAL_REJECTED, to_status=Subtask.Status.REQUESTING_APPROVAL)
    ])

    MULTIPLEX_REMOVE = TransitionPack([
        Transition(from_status=Subtask.Status.CONTESTED, to_status=Subtask.Status.REMOVED)
    ])

    MULTIPLEX_UNDO = TransitionPack([
        Transition(from_status=Subtask.Status.IN_PROGRESS, to_status=Subtask.Status.CONTESTED),
        Transition(from_status=Subtask.Status.IN_PROGRESS, to_status=Subtask.Status.DECLINED),
        Transition(from_status=Subtask.Status.CONTESTED, to_status=Subtask.Status.DECLINED),
        Transition(from_status=Subtask.Status.INSPECTION_REJECTED, to_status=Subtask.Status.UNDER_INSPECTION),
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.UNDER_INSPECTION),
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    MULTIPLEX_CONTEST = TransitionPack([
        Transition(from_status=Subtask.Status.DECLINED, to_status=Subtask.Status.CONTESTED)
    ])

    MULTIPLEX_REQUESTING_APPROVAL = TransitionPack([
        Transition(from_status=Subtask.Status.UNDER_INSPECTION, to_status=Subtask.Status.REQUESTING_APPROVAL),
        Transition(from_status=Subtask.Status.CLOSED, to_status=Subtask.Status.REQUESTING_APPROVAL),
        Transition(from_status=Subtask.Status.CONTESTED, to_status=Subtask.Status.REQUESTING_APPROVAL),
        Transition(from_status=Subtask.Status.DECLINED, to_status=Subtask.Status.REQUESTING_APPROVAL),
        Transition(from_status=Subtask.Status.IN_PROGRESS, to_status=Subtask.Status.REQUESTING_APPROVAL),
        Transition(from_status=Subtask.Status.INSPECTION_REJECTED, to_status=Subtask.Status.REQUESTING_APPROVAL),
        Transition(from_status=Subtask.Status.REQUESTED_APPROVAL_REJECTED, to_status=Subtask.Status.REQUESTING_APPROVAL)
    ])

    MULTIPLEX_RE_OPEN = TransitionPack([
        Transition(from_status=Subtask.Status.CLOSED, to_status=Subtask.Status.IN_PROGRESS),
        Transition(from_status=Subtask.Status.CONTESTED, to_status=Subtask.Status.IN_PROGRESS),
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.IN_PROGRESS),
        Transition(from_status=Subtask.Status.DECLINED, to_status=Subtask.Status.IN_PROGRESS),
        Transition(from_status=Subtask.Status.REQUESTED_APPROVAL_REJECTED, to_status=Subtask.Status.IN_PROGRESS)
    ])

    MULTIPLEX_CLOSE = TransitionPack([
        Transition(from_status=Subtask.Status.IN_PROGRESS, to_status=Subtask.Status.CLOSED),
        Transition(from_status=Subtask.Status.INSPECTION_REJECTED, to_status=Subtask.Status.CLOSED),
        Transition(from_status=Subtask.Status.CONTESTED, to_status=Subtask.Status.CLOSED),
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.CLOSED),
        Transition(from_status=Subtask.Status.DECLINED, to_status=Subtask.Status.CLOSED),
        Transition(from_status=Subtask.Status.REMOVED, to_status=Subtask.Status.CLOSED),
        Transition(from_status=Subtask.Status.REQUESTED_APPROVAL_REJECTED, to_status=Subtask.Status.CLOSED),
        Transition(from_status=Subtask.Status.UNDER_INSPECTION, to_status=Subtask.Status.CLOSED),
    ])

    # Do not include this pack to other transition packs. It's redundant.
    MULTIPLEX_SYNC_CREATE_FULL_DATA_COPY_WHITELISTED_TRANSITIONS = TransitionPack([
        Transition(from_status=Subtask.Status.CLOSED, to_status=Subtask.Status.IN_PROGRESS),
        Transition(from_status=Subtask.Status.DECLINED, to_status=Subtask.Status.CONTESTED),
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.REQUESTED_APPROVAL_REJECTED),
        Transition(from_status=Subtask.Status.REQUESTED_APPROVAL_REJECTED, to_status=Subtask.Status.REQUESTING_APPROVAL),
    ]) + MULTIPLEX_REQUESTING_APPROVAL + MULTIPLEX_CLOSE

    MULTIPLEX_TRANSITIONS = MULTIPLEX_RE_OPEN + MULTIPLEX_UNDO + MULTIPLEX_REJECT + MULTIPLEX_CLOSE + \
        MULTIPLEX_REMOVE + MULTIPLEX_REQUESTING_APPROVAL + MULTIPLEX_CONTEST

    MULTIPLEX_CONFIRMED_UPDATE = MULTIPLEX_RE_OPEN + MULTIPLEX_REJECT + \
        MULTIPLEX_REMOVE + MULTIPLEX_REQUESTING_APPROVAL + MULTIPLEX_CONTEST

    SUBCONTRACTOR_REJECT = TransitionPack([
        Transition(from_status=Subtask.Status.INSPECTION_REJECTED, to_status=Subtask.Status.CONTESTED),
    ])

    SUBCONTRACTOR_UNDO = TransitionPack([
        Transition(from_status=Subtask.Status.DECLINED, to_status=Subtask.Status.IN_PROGRESS),
        Transition(from_status=Subtask.Status.UNDER_INSPECTION, to_status=Subtask.Status.IN_PROGRESS),
    ])

    SUBCONTRACTOR_CLOSE_OUT = TransitionPack([
        Transition(from_status=Subtask.Status.IN_PROGRESS, to_status=Subtask.Status.UNDER_INSPECTION),
        Transition(from_status=Subtask.Status.INSPECTION_REJECTED, to_status=Subtask.Status.UNDER_INSPECTION),
    ])

    SUBCONTRACTOR_DECLINE = TransitionPack([
        Transition(from_status=Subtask.Status.IN_PROGRESS, to_status=Subtask.Status.DECLINED),
        Transition(from_status=Subtask.Status.INSPECTION_REJECTED, to_status=Subtask.Status.DECLINED)
    ])

    CLIENTS_CLOSE = TransitionPack([
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.CLOSED)
    ])

    CLIENTS_REJECT = TransitionPack([
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.REQUESTED_APPROVAL_REJECTED)
    ])

    CLIENTS_REMOVE = TransitionPack([
        Transition(from_status=Subtask.Status.CONTESTED, to_status=Subtask.Status.REMOVED),
        Transition(from_status=Subtask.Status.IN_PROGRESS, to_status=Subtask.Status.REMOVED),
        Transition(from_status=Subtask.Status.REQUESTING_APPROVAL, to_status=Subtask.Status.REMOVED),
        Transition(from_status=Subtask.Status.INSPECTION_REJECTED, to_status=Subtask.Status.REMOVED),
        Transition(from_status=Subtask.Status.UNDER_INSPECTION, to_status=Subtask.Status.REMOVED),
        Transition(from_status=Subtask.Status.CLOSED, to_status=Subtask.Status.REMOVED),
        Transition(from_status=Subtask.Status.DECLINED, to_status=Subtask.Status.REMOVED),
        Transition(from_status=Subtask.Status.REMOVED, to_status=Subtask.Status.REMOVED),
    ])

    CLIENTS_CONFIRMED_UPDATE = CLIENTS_REJECT + CLIENTS_SYNCED_REMOVE + CLIENTS_SYNCED_CLOSE_OUT

    STATUS_TRANSITIONS = {
        User.Group.SUBCONTRACTOR.value: SUBCONTRACTOR_REJECT + SUBCONTRACTOR_CLOSE_OUT + SUBCONTRACTOR_UNDO + SUBCONTRACTOR_DECLINE,
        User.Group.COMPANY_ADMIN.value: MULTIPLEX_TRANSITIONS,
        User.Group.MANAGER.value: MULTIPLEX_TRANSITIONS,
        User.Group.ADMIN.value: MULTIPLEX_TRANSITIONS,
        User.Group.CLIENT.value: CLIENTS_CLOSE + CLIENTS_REMOVE,
        User.Group.CONSULTANT.value: CLIENTS_CLOSE + CLIENTS_REMOVE
    }

    CONFIRMED_UPDATE_TRANSITIONS = {
        User.Group.SUBCONTRACTOR.value: SUBCONTRACTOR_REJECT + SUBCONTRACTOR_CLOSE_OUT + SUBCONTRACTOR_DECLINE,
        User.Group.COMPANY_ADMIN.value: MULTIPLEX_CONFIRMED_UPDATE,
        User.Group.MANAGER.value: MULTIPLEX_CONFIRMED_UPDATE,
        User.Group.ADMIN.value: MULTIPLEX_CONFIRMED_UPDATE,
        User.Group.CLIENT.value: CLIENTS_CONFIRMED_UPDATE,
        User.Group.CONSULTANT.value: CLIENTS_CONFIRMED_UPDATE,
    }

    UNDO_TRANSITIONS = {
        User.Group.SUBCONTRACTOR.value: SUBCONTRACTOR_UNDO,
        User.Group.MANAGER.value: MULTIPLEX_UNDO,
        User.Group.ADMIN.value: MULTIPLEX_UNDO,
        User.Group.COMPANY_ADMIN.value: MULTIPLEX_UNDO
    }

    SYNC_CREATE_FULL_DATA_COPY_WHITELISTED_TRANSITIONS = {
        User.Group.MANAGER.value: MULTIPLEX_SYNC_CREATE_FULL_DATA_COPY_WHITELISTED_TRANSITIONS,
        User.Group.ADMIN.value: MULTIPLEX_SYNC_CREATE_FULL_DATA_COPY_WHITELISTED_TRANSITIONS,
        User.Group.COMPANY_ADMIN.value: MULTIPLEX_SYNC_CREATE_FULL_DATA_COPY_WHITELISTED_TRANSITIONS,
    }

    def __init__(self, update, user):
        super().__init__(update, user)
        subtask = update['subtask'] \
            if isinstance(update['subtask'], BaseModel) \
            else Subtask.objects.filter(pk=update['subtask']).first()

        if not subtask.quality_issue:
            self.MULTIPLEX_TRANSITIONS = self.MULTIPLEX_TRANSITIONS + TransitionPack([
                Transition(from_status=Subtask.Status.DECLINED, to_status=Subtask.Status.REMOVED),
                Transition(from_status=Subtask.Status.IN_PROGRESS, to_status=Subtask.Status.REMOVED),
            ])
            self._refresh_multiplex_status_transitions()

    def is_valid_change(self):
        if self.transition.is_update():
            return True

        if self.user.is_staff and not self.transition.from_status:
            return True

        status_transitions = self.STATUS_TRANSITIONS.get(self.user.group.pk, [])

        return self.transition in status_transitions

    def is_reopen(self):
        return self.transition in self.MULTIPLEX_RE_OPEN

    def is_reject(self):
        return self.transition in self.MULTIPLEX_REJECT + self.CLIENTS_REJECT

    def is_new(self):
        return not self.transition.from_status

    def is_requesting_approval(self):
        return self.transition in self.MULTIPLEX_REQUESTING_APPROVAL

    def is_requesting_approval_undo(self):
        return self.transition in self.MULTIPLEX_UNDO

    def does_subcontractor_action_require_quality_issue_transition_into_in_progress(self):
        return self.transition in \
               self.SUBCONTRACTOR_CLOSE_OUT + self.SUBCONTRACTOR_UNDO + self.SUBCONTRACTOR_REJECT

    def get_confirmed_transitions(self):
        return self.SUBCONTRACTOR_REJECT + self.SUBCONTRACTOR_CLOSE_OUT + self.MULTIPLEX_CONFIRMED_UPDATE

    def _refresh_multiplex_status_transitions(self):
        self.STATUS_TRANSITIONS[User.Group.COMPANY_ADMIN.value] = self.MULTIPLEX_TRANSITIONS
        self.STATUS_TRANSITIONS[User.Group.ADMIN.value] = self.MULTIPLEX_TRANSITIONS
        self.STATUS_TRANSITIONS[User.Group.MANAGER.value] = self.MULTIPLEX_TRANSITIONS

    def is_sync_create_full_data_copy_allowed(self) -> bool:
        transitions = self.SYNC_CREATE_FULL_DATA_COPY_WHITELISTED_TRANSITIONS.get(self.user.group.pk)
        return self.transition in transitions if transitions else False

    def is_sync_create_update_files_copy_allowed(self) -> bool:
        return self.transition.from_status == self.transition.to_status or \
               self.is_sync_create_full_data_copy_allowed() if self.user.is_multiplex else False
