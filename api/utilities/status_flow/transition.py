class Transition:
    def __init__(self, from_status, to_status):
        self.from_status = from_status
        self.to_status = to_status

    def __str__(self):
        return f'{self.from_status if self.from_status is not None else ""}-{self.to_status}'

    def is_update(self):
        return self.from_status == self.to_status

    def undo(self):
        return self.__class__(self.to_status, self.from_status)


class TransitionPack:
    def __init__(self, transitions: list):
        self.transitions = transitions

    def __add__(self, other_transition_pack):
        return self.__class__(self.transitions + other_transition_pack.transitions)

    def __contains__(self, status_transition):
        status_transition = str(status_transition) if isinstance(status_transition, Transition) else status_transition
        result = filter(lambda transition: status_transition == str(transition), self.transitions)

        return len(list(result)) > 0

    def __iter__(self):
        for transition in self.transitions:
            yield str(transition)

    def __len__(self):
        return len(self.transitions)

    def get_undo(self):
        return self.__class__(list(map(lambda transition: transition.undo(), self.transitions)))

    def get_with_from_status(self, status):
        return self.__class__(list(
            filter(lambda transition: transition.from_status == status, self.transitions)
        ))

    def get_with_to_status(self, status):
        return self.__class__(list(
            filter(lambda transition: transition.to_status == status, self.transitions)
        ))
