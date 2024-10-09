from rest_framework import status
from rest_framework.response import Response

from api.http.filters.locations.locations_area_filter import LocationsAreaFilter
from api.http.views import LocationsView


class LocationsAreaView(LocationsView):
    filterset_class = LocationsAreaFilter

    def list(self, request, *args, **kwargs):
        filters, kwfilters = self._get_locations_filters()
        queryset = self.filter_queryset(self.get_queryset().filter(*filters, **kwfilters)).distinct('area').values('area')

        if request.query_params.get('get_total_items_count'):
            return Response({
                'total_items': self.paginator.django_paginator_class(queryset, self.paginator.page_size).get_total_items_count(),
            })

        page = self.paginate_queryset(queryset)

        if page is not None:
            return self.get_paginated_response(page)

        return Response(data=list(queryset), status=status.HTTP_200_OK)
