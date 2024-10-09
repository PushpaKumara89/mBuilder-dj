from django.db.models import When, Value, Q
from typing import List


def numerate_when_expressions(expressions: List[Q], number_start: int = 1) -> List[When]:
    return [When(expression, then=Value(i)) for i, expression in enumerate(expressions, start=number_start)]
