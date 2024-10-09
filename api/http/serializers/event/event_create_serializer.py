from api.http.serializers.event.event_serializer import EventSerializer
from api.models import Event


class EventCreateSerializer(EventSerializer):
    class Meta:
        model = Event
        fields = ('events',)

    events = EventSerializer(many=True)
