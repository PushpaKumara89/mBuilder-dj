from rest_framework.serializers import ListSerializer


class BaseListSyncSerializer(ListSerializer):
    _existing_entities_data: list
    _new_entities_data: list
    _fields_to_update: list
    _ignore_on_update = list()
    _is_validation_required = True

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def sync(self) -> None:
        self._delete_nonexistent()
        if hasattr(self, 'initial_data') and len(self.initial_data) > 0:
            self._validate()
            self._divide_validated_data()
            self._update_entities()
            self._create_entities()

    def _validate(self) -> None:
        if self._is_validation_required:
            self.is_valid(raise_exception=True)
        else:
            self._validated_data = self.initial_data

    def _delete_nonexistent(self) -> None:
        data = [] if not self.initial_data else self.initial_data
        existing_ids = [entity['id'] for entity in data if 'id' in entity]
        self.child.Meta.model.objects.exclude(pk__in=existing_ids).delete()

    def _create_entities(self) -> None:
        new_entities = [self.child.Meta.model(**entity_data) for entity_data in self._new_entities_data]
        self.child.Meta.model.objects.bulk_create(new_entities)

    def _update_entities(self) -> None:
        mapping_data = {item['id']: self._exclude_id(item) for item in self._existing_entities_data}
        entities_ids = [key for key, value in mapping_data.items()]
        entities = self.child.Meta.model.objects.filter(pk__in=entities_ids).all()
        updated_entities = list()

        for entity_id, data in mapping_data.items():
            entity = next(item for item in entities if entity_id == item.pk)
            for field_name, value in data.items():
                if field_name not in self._ignore_on_update:
                    setattr(entity, field_name, value)
            updated_entities.append(entity)

        self.child.Meta.model.objects.bulk_update(updated_entities, self._fields_to_update)

    def _exclude_id(self, item: dict) -> dict:
        return {key: value for key, value in item.items() if key != 'id'}

    def _divide_validated_data(self) -> None:
        self._existing_entities_data = list()
        self._new_entities_data = list()

        for elem in self.validated_data:
            if 'id' in elem and elem['id'] is not None:
                self._existing_entities_data.append(elem)
            else:
                self._new_entities_data.append(elem)
