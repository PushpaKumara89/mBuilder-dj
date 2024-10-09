from rest_framework import serializers

from api.http.serializers import AssetHandoverSerializer, AssetHandoverDocumentSerializer, \
    AssetHandoverInformationSerializer
from api.http.serializers.asset_handover import AssetHandoverInformationEditableDataSerializer
from api.http.serializers.asset_handover.asset_handover_document.asset_handover_document_editable_data_serializer import \
    AssetHandoverDocumentEditableDataSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandover, PackageActivity, LocationMatrixPackage, AssetHandoverDocument
from django.db.models import Exists, OuterRef

from api.queues.asset_handover_statistics import undelete_statistics_on_asset_handover_undelete
from api.queues.handover_document import undelete_handover_document_on_asset_handover_undelete


class AssetHandoverCreateSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandover
        fields = ('id', 'building', 'level', 'area', 'package_activity', 'documents',
                  'asset_handover_information', 'created_at', 'updated_at',)

    building = serializers.CharField(required=True, max_length=255, allow_null=True)
    level = serializers.CharField(required=True, max_length=255, allow_null=True)
    area = serializers.CharField(required=True, max_length=255, allow_null=True)
    package_activity = serializers.PrimaryKeyRelatedField(queryset=PackageActivity.objects.all(), required=True)
    documents = AssetHandoverDocumentEditableDataSerializer(many=True, required=True)
    asset_handover_information = AssetHandoverInformationEditableDataSerializer(required=False)

    def create(self, validated_data):
        restored_asset_handovers, new_asset_handovers = self.__create_asset_handovers()

        self.__create_asset_handover_documents(new_asset_handovers)
        self.__create_asset_handover_information(new_asset_handovers)

        return restored_asset_handovers + new_asset_handovers

    def __create_asset_handovers(self):
        location_matrix_ids = self.__get_location_matrix_ids()

        if not location_matrix_ids:
            return [], []

        asset_handover_creation_data = self.__get_asset_handover_creation_data(location_matrix_ids)
        restored_asset_handovers, deleted_asset_handovers_location_matrix_ids = self.__restore_deleted_asset_handovers(location_matrix_ids)
        asset_handover_creation_data = self.__remove_from_creation_data_restored_duplications(
            asset_handover_creation_data, deleted_asset_handovers_location_matrix_ids)

        serializer = AssetHandoverSerializer(data=asset_handover_creation_data, many=True)
        serializer.is_valid(raise_exception=True)

        return restored_asset_handovers, serializer.create(serializer.validated_data)

    def __get_asset_handover_creation_data(self, location_matrix_ids):
        return list(
            map(
                lambda location_matrix_id: {
                    'location_matrix': location_matrix_id,
                    'package_activity': self.validated_data['package_activity'].pk,
                    'project': self.context['view'].kwargs['project_pk']
                },
                location_matrix_ids
            )
        )

    def __get_location_matrix_ids(self):
        filters = {
            'location_matrix__project_id': self.context['view'].kwargs['project_pk'],
            'enabled': True,
            'asset_handover_exists': False,
            'location_matrix__deleted__isnull': True,
            'package_activity_id': self.validated_data['package_activity'].pk
        }

        if building := self.validated_data['building']:
            filters['location_matrix__building'] = building

        if level := self.validated_data['level']:
            filters['location_matrix__level'] = level

        if area := self.validated_data['area']:
            filters['location_matrix__area'] = area

        return list(
            LocationMatrixPackage.objects.annotate(
                asset_handover_exists=Exists(AssetHandover.objects.filter(
                    location_matrix_id=OuterRef('location_matrix_id'),
                    package_activity_id=self.validated_data['package_activity'].pk,
                    deleted=None
                ))
            ).filter(**filters).values_list('location_matrix_id', flat=True)
        )

    def __create_asset_handover_documents(self, asset_handovers):
        documents = []

        for asset_handover in asset_handovers:
            prepared_data_for_creation_asset_handover_documents = list(
                map(
                    lambda document: {
                        'document_type': document['document_type'].pk,
                        'number_required_files': document['number_required_files'],
                        'asset_handover': asset_handover.pk
                    },
                    self.validated_data['documents']
                )
            )

            documents = [*documents, *prepared_data_for_creation_asset_handover_documents]

        if documents:
            serializer = AssetHandoverDocumentSerializer(data=documents, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.create(serializer.validated_data)

    def __create_asset_handover_information(self, asset_handovers):
        if 'asset_handover_information' in self.validated_data:
            asset_handover_information = list(
                map(
                    lambda asset_handover: {
                        **self.validated_data['asset_handover_information'],
                        'asset_handover': asset_handover
                    },
                    asset_handovers
                )
            )

            if asset_handover_information:
                AssetHandoverInformationSerializer(many=True).create(asset_handover_information)

    def __restore_deleted_asset_handovers(self, location_matrix_ids):
        deleted_asset_handover = self.__get_deleted_asset_handovers(location_matrix_ids)

        if deleted_asset_handover:
            deleted_asset_handover_location_matrix_ids, deleted_asset_handover_ids = self.__get_asset_handover_key_values(deleted_asset_handover)
            deleted_asset_handover.update(deleted=None)

            self.__update_restored_asset_handover_documents(deleted_asset_handover_ids)
            restored_asset_handovers = list(AssetHandover.objects.filter(id__in=deleted_asset_handover_ids).all())
            undelete_handover_document_on_asset_handover_undelete(restored_asset_handovers)
            undelete_statistics_on_asset_handover_undelete(restored_asset_handovers)

            return restored_asset_handovers, deleted_asset_handover_location_matrix_ids

        return [], []

    def __get_deleted_asset_handovers(self, location_matrix_ids):
        return AssetHandover.deleted_objects.filter(
            location_matrix_id__in=location_matrix_ids, package_activity_id=self.validated_data['package_activity'].pk
        ).all()

    def __get_asset_handover_key_values(self, deleted_asset_handover):
        deleted_asset_handover_key_values = deleted_asset_handover.values('location_matrix_id', 'id')
        asset_handover_location_matrix_ids = []
        asset_handover_ids = []

        for asset_handover in deleted_asset_handover_key_values:
            asset_handover_location_matrix_ids.append(asset_handover['location_matrix_id'])
            asset_handover_ids.append(asset_handover['id'])

        return asset_handover_location_matrix_ids, asset_handover_ids

    def __remove_from_creation_data_restored_duplications(self, new_asset_handovers_data, location_matrix_ids):
        return list(
            filter(
                lambda asset_handover_data: asset_handover_data['location_matrix'] not in location_matrix_ids,
                new_asset_handovers_data
            )
        )

    def __update_restored_asset_handover_documents(self, deleted_asset_handover_ids):
        for document in self.validated_data['documents']:
            AssetHandoverDocument.objects.filter(
                asset_handover_id__in=deleted_asset_handover_ids, document_type=document['document_type']
            ).update(number_required_files=document['number_required_files'])
