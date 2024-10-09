from enum import Enum


class SummaryType(Enum):
    daily = 'daily'
    weekly = 'weekly'

    def __str__(self):
        return self.value
