from django.db.models import Func, F, Value, FloatField, When, Case
from django.db.models.functions import NullIf, Cast


# Levels may have the next format: [digit][?letter][?digit]. For instance, "10", or "9M", or "4N5".
# Firstly, sort levels by the first digit, after that - alphabetically by letter, and in the and - by second digit
def annotate_location_matrix_level_parts(queryset, level_field='level'):
    return queryset.annotate(
        level_number=Case(
            # We cast all values to the float type to sort by uniform field.
            When(
                # Format levels with 0[letter][digit] structure to float.
                # For example, "0M3" -> 0.3 or "-0u2" -> -0.2 .
                **{level_field + '__iregex': r'(^-\d.)|(^0.)'},
                then=Cast(
                    Func(Func(F(level_field), Value('[a-zA-Z]+'), Value('.'), function='regexp_replace'), Value('0001'), function='concat'),
                    FloatField()
                ),
            ),
            # We get only the first digit. It doesn't matter if it's positive or negative.
            # For instance, "2T0" -> 2, or "-4Y" -> -4, or "0Q3" -> 0 .
            default=Cast(
                Func(F(level_field), Value('^(-?\d+)'), function='substring'),
                FloatField()
            ),
        ),
        # We get only "letter-part" of level sting format [digit][?LETTER][?digit].
        # If a level contains only digits, replace it to null value.
        # It helps us to sort rows in the right alphabetically order.
        level_postfix=NullIf(Func(F(level_field), Value('^(-?\d+)'), Value(''), function='regexp_replace'), Value('')),
    )
