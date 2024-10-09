from api.http.serializers.base_list_sync_serializer import BaseListSyncSerializer


class DependentEntityListSyncSerializer(BaseListSyncSerializer):
    _parent_relation_field: str

    def _delete_nonexistent(self) -> None:
        data = self.initial_data if hasattr(self, 'initial_data') else []
        existing_ids = [entity['id'] for entity in data if 'id' in entity]
        filter_parameters = {self._parent_relation_field: self.child.parent_id}

        self.child.Meta.model.objects.exclude(pk__in=existing_ids).filter(**filter_parameters).delete()

    def _divide_validated_data(self) -> None:
        self._existing_entities_data = list()
        self._new_entities_data = list()

        for elem in self.validated_data:
            if 'id' in elem and elem['id'] is not None:
                self._existing_entities_data.append(elem)
            else:
                elem[self._parent_relation_field] = self.child.parent_id
                self._new_entities_data.append(elem)
