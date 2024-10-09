from datetime import datetime
from enum import Enum

from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.media.media_serializer import MediaSerializer
from api.http.serializers.package_handover.package_handover_document_media_update.package_handover_document_media_update_serializer import \
    PackageHandoverDocumentMediaUpdateSerializer
from api.models import PackageHandoverDocumentMedia
from api.utilities.time_utilities import change_timezone_to_london


class PackageHandoverDocumentMediaReportSerializer(BaseModelSerializer):
    class ExportProducer(Enum):
        CSV = 1

    class Meta:
        model = PackageHandoverDocumentMedia
        fields = ('id', 'uid', 'package_handover_document_type', 'package',
                  'package_activity_id', 'package_activity', 'information')
        expandable_fields = {
            'expanded_user_identified': (serializers.SerializerMethodField, {'method_name': 'user_identified'}),
            'expanded_status_by': (serializers.SerializerMethodField, {'method_name': 'status_by'}),
            'expanded_status_comments': (serializers.SerializerMethodField, {'method_name': 'status_comments'}),
            'expanded_status_change_date': (serializers.SerializerMethodField, {'method_name': 'status_change_date'}),
            'expanded_status_change_time': (serializers.SerializerMethodField, {'method_name': 'status_change_time'}),

            'expanded_last_uploaded_date': (serializers.SerializerMethodField, {'method_name': 'last_uploaded_date'}),
            'expanded_last_uploaded_time': (serializers.SerializerMethodField, {'method_name': 'last_uploaded_time'}),
            'expanded_last_modified_date': (serializers.SerializerMethodField, {'method_name': 'last_modified_date'}),
            'expanded_last_modified_time': (serializers.SerializerMethodField, {'method_name': 'last_modified_time'}),
            'expanded_completed_date': (serializers.SerializerMethodField, {'method_name': 'completed_date'}),
            'expanded_completed_time': (serializers.SerializerMethodField, {'method_name': 'completed_time'}),

            'expanded_title': (serializers.SerializerMethodField, {'method_name': 'title'}),
            'expanded_extension': (serializers.SerializerMethodField, {'method_name': 'extension'}),
            'expanded_status_history': (serializers.SerializerMethodField, {'method_name': 'status_history'}),
            'expanded_status_view': (serializers.SerializerMethodField, {'method_name': 'status_view'}),
            'expanded_company': (serializers.SerializerMethodField, {'method_name': 'company'}),
        }

    package_handover_document_type = serializers.CharField(source='package_handover_document.package_handover_document_type.name', read_only=True)
    package = serializers.CharField(source='package_handover_document.package_handover.package_matrix.package.name', read_only=True)
    package_activity_id = serializers.CharField(source='package_handover_document.package_handover.package_matrix.package_activity.activity_id', read_only=True)
    package_activity = serializers.CharField(source='package_handover_document.package_handover.package_matrix.package_activity.name', read_only=True)

    def __init__(self, *args, export_producer: ExportProducer = ExportProducer.CSV, **kwargs):
        self.export_producer = export_producer

        super().__init__(*args, **kwargs)

    def company(self, obj: PackageHandoverDocumentMedia):
        update = self.__get_last_uploaded_media_update(obj)

        return update.company.name if update else ''

    def status_view(self, obj: PackageHandoverDocumentMedia):
        return dict(PackageHandoverDocumentMedia.Status.choices)[obj.status]

    def status_history(self, obj: PackageHandoverDocumentMedia):
        result = ''

        media_updates_query = obj.packagehandoverdocumentmediaupdate_set.all()

        serialized_history_items = PackageHandoverDocumentMediaUpdateSerializer(
            media_updates_query,
            many=True
        ).data

        for count, item in enumerate(serialized_history_items, start=1):
            status = item.get('new_data', {}).get('status')
            result += f'{count}) {dict(PackageHandoverDocumentMedia.Status.choices)[status]}\n'

        return result

    def user_identified(self, obj: PackageHandoverDocumentMedia):
        data_media_update = PackageHandoverDocumentMediaUpdateSerializer(
            self.__get_last_uploaded_media_update(obj),
            expand=['expanded_user.expanded_user_company']
        ).data

        return self.__get_user_view(data_media_update['expanded_user']) if data_media_update.get('expanded_user') else ''

    def last_uploaded_date(self, obj: PackageHandoverDocumentMedia):
        media = self.__get_last_uploaded_media_update(obj)

        return self.__get_date_view(media.created_at) if media else ''

    def last_uploaded_time(self, obj: PackageHandoverDocumentMedia):
        media = self.__get_last_uploaded_media_update(obj)

        return self.__get_time_view(media.created_at) if media else ''

    def last_modified_date(self, obj: PackageHandoverDocumentMedia):
        media = self.__get_last_media_update(obj)

        return self.__get_date_view(media.created_at) if media else ''

    def last_modified_time(self, obj: PackageHandoverDocumentMedia):
        media = self.__get_last_media_update(obj)

        return self.__get_time_view(media.created_at) if media else ''

    def completed_date(self, obj: PackageHandoverDocumentMedia):
        media = self.__get_accepted_media_update(obj)

        return self.__get_date_view(media.created_at) if media else ''

    def completed_time(self, obj: PackageHandoverDocumentMedia):
        media = self.__get_accepted_media_update(obj)

        return self.__get_time_view(media.created_at) if media else ''

    def status_by(self, obj: PackageHandoverDocumentMedia):
        media_updates_query = obj.packagehandoverdocumentmediaupdate_set.select_related('user__company').all()

        data_media_updates = PackageHandoverDocumentMediaUpdateSerializer(
            media_updates_query,
            many=True,
            expand=['expanded_user.expanded_user_company']
        ).data

        result = ''
        for count, data_media_update in enumerate(data_media_updates, start=1):
            result += f'{count}) {self.__get_user_view(data_media_update["expanded_user"])}\n'

        return result

    def status_comments(self, obj: PackageHandoverDocumentMedia):
        media_updates_query = obj.packagehandoverdocumentmediaupdate_set.all()

        data_media_updates = PackageHandoverDocumentMediaUpdateSerializer(
            media_updates_query,
            many=True,
            expand=['expanded_user.expanded_user_company']
        ).data

        result = ''
        for count, data_media_update in enumerate(data_media_updates, start=1):
            result += f'{count}) {data_media_update["comment"] if data_media_update["comment"] else ""}\n'

        return result

    def status_change_date(self, obj: PackageHandoverDocumentMedia):
        media_updates_query = obj.packagehandoverdocumentmediaupdate_set.all()

        result = ''
        for count, media_update in enumerate(media_updates_query, start=1):
            result += f'{count}) {self.__get_date_view(media_update.created_at)}\n'

        return result

    def status_change_time(self, obj: PackageHandoverDocumentMedia):
        media_updates_query = obj.packagehandoverdocumentmediaupdate_set.all()

        result = ''
        for count, media_update in enumerate(media_updates_query, start=1):
            result += f'{count}) {self.__get_time_view(media_update.created_at)}\n'

        return result

    def title(self, obj: PackageHandoverDocumentMedia):
        data_media = MediaSerializer(obj.media).data

        return data_media['name']

    def extension(self, obj: PackageHandoverDocumentMedia):
        data_media = MediaSerializer(obj.media, expand=['expanded_extension']).data

        return f'.{data_media["expanded_extension"]}'

    def __get_user_view(self, data_user: dict):
        return '%s %s (%s)' % (data_user['first_name'], data_user['last_name'], data_user['expanded_user_company']['name'])

    def __get_date_view(self, created_at: datetime):
        created_date = change_timezone_to_london(created_at)
        return created_date.strftime('%d/%m/%Y')

    def __get_time_view(self, created_at: datetime):
        created_date = change_timezone_to_london(created_at)
        return created_date.strftime('%I:%M %p')

    def __get_uploaded_media_query(self, media: PackageHandoverDocumentMedia):
        return media.\
            packagehandoverdocumentmediaupdate_set.\
            filter(new_data__media__isnull=False).\
            all()

    def __get_last_uploaded_media_update(self, media: PackageHandoverDocumentMedia):
        return self.__get_uploaded_media_query(media).\
            select_related('user__company').\
            order_by('-created_at').\
            first()

    def __get_last_media_update(self, media: PackageHandoverDocumentMedia):
        return media.\
            packagehandoverdocumentmediaupdate_set.\
            order_by('-created_at').\
            first()

    def __get_accepted_media_update(self, media: PackageHandoverDocumentMedia):
        return media.\
            packagehandoverdocumentmediaupdate_set. \
            filter(new_data__status=PackageHandoverDocumentMedia.Status.ACCEPTED.value). \
            order_by('-created_at'). \
            first()
