from django_filters.widgets import QueryArrayWidget

from api.http.filters import LocationsFilter
from api.http.filters.base_filters.char_in_filter import CharInFilter


class LocationsAreaFilter(LocationsFilter):
    exclude = CharInFilter(field_name='area', exclude=True, widget=QueryArrayWidget)
