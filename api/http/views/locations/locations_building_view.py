from django.db import connection
from rest_framework import status
from rest_framework.response import Response

from api.http.views import LocationsView


class LocationsBuildingView(LocationsView):
    def list(self, request, *args, **kwargs):
        filters, kwfilters = self._get_locations_filters(use_raw_values=True)
        buildings = (
            self.filter_queryset(self.get_queryset().filter(*filters, **kwfilters))
                .distinct('building')
                .order_by('building')
                .values_list('building', flat=True)
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    with recursive t as (select min(building) as building
                             from location_matrix
                             where project_id = %s and deleted is null
                             union all
                             select (select min(building) from location_matrix where building > t.building and project_id = %s and deleted is null)
                             from t
                             where t.building is not null)
                    select t.building from t where t.building is not null and t.building = ANY(%s)""",
                (self.kwargs['project_pk'], self.kwargs['project_pk'], list(buildings))
            )
            result = self.dictfetchall(cursor)

        page = self.paginate_queryset(result)

        if page is not None:
            return self.get_paginated_response(page)

        return Response(data=list(result), status=status.HTTP_200_OK)

    def dictfetchall(self, cursor):
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
