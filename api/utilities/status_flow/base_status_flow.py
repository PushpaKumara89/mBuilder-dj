from abc import abstractmethod, ABC
from api.utilities.status_flow.transition import Transition


class BaseStatusFlow(ABC):
    def __init__(self, update, user):
        self.user = user
        self.transition = Transition(update['old_data'].get('status'), update['new_data']['status'])
        self.new_data = update['new_data']

    CONFIRMED_UPDATE_TRANSITIONS = {}

    STATUS_TRANSITIONS = {}

    def is_confirmed_update(self):
        """
        An update is for transition with confirmation only in the case when `new_data`
        contains only one `status` field.
        """
        confirmed_updates = self.CONFIRMED_UPDATE_TRANSITIONS.get(self.user.group.pk, [])
        return 'status' in self.new_data and \
               len(self.new_data) == 1 and \
               self.transition in confirmed_updates

    def is_update(self):
        return self.transition.is_update()

    def is_undo(self):
        transitions = self.STATUS_TRANSITIONS.get(self.user.group.pk, [])

        return self.transition in transitions.get_undo() if len(transitions) > 0 else False

    @abstractmethod
    def is_valid_change(self):
        ...

    @abstractmethod
    def get_confirmed_transitions(self):
        ...

    def get_confirmed_transitions_filtered_by_to_status(self):
        return self.get_confirmed_transitions().get_with_to_status(self.transition.to_status)

    def filter_confirmed_transitions_by_from_status(self):
        return self.get_confirmed_transitions().get_with_to_status(self.transition.from_status)
