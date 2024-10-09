from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return [item.value for item in cls]
