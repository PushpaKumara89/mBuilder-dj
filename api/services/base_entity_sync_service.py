from typing import Any, List, Dict


class BaseEntitySyncService:
    existing_entities_data: List
    new_entities_data: List
    ignore_on_update: List = []

    def __init__(self,
                 model: Any,
                 validated_data: List[Dict] = None,
                 initial_data: List[Dict] = None,
                 fields_to_update: List = None,
                 is_validation_required: bool = True) -> None:
        self.model = model
        self.validated_data = validated_data or []
        self.initial_data = initial_data or []
        self.fields_to_update = fields_to_update
        self.is_validation_required = is_validation_required

    def sync(self, delete_nonexistent: bool = True) -> None:
        if delete_nonexistent:
            self.delete_nonexistent()
        if hasattr(self, 'initial_data') and len(self.initial_data) > 0:
            self._divide_validated_data()
            self._update_entities()
            self._create_entities()

    def delete_nonexistent(self) -> None:
        self.model.objects.exclude(pk__in=[entity['id'] for entity in self.initial_data if 'id' in entity]).delete()

    def _create_entities(self) -> None:
        new_entities = [self.model(**entity_data) for entity_data in self.new_entities_data]
        self.model.objects.bulk_create(new_entities)

    def _update_entities(self) -> None:
        mapping_data = {item['id']: self._exclude_id(item) for item in self.existing_entities_data}
        entities_ids = list(mapping_data.keys())
        entities = self.model.objects.filter(pk__in=entities_ids).all()
        updated_entities = []

        for entity_id, data in mapping_data.items():
            entity = next(item for item in entities if entity_id == item.pk)
            for field_name, value in data.items():
                if field_name not in self.ignore_on_update:
                    setattr(entity, field_name, value)
            updated_entities.append(entity)

        self.model.objects.bulk_update(updated_entities, self.fields_to_update)
    
    @staticmethod
    def _exclude_id(item: Dict) -> Dict:
        return {key: value for key, value in item.items() if key != 'id'}

    def _divide_validated_data(self) -> None:
        self.existing_entities_data = []
        self.new_entities_data = []

        for elem in self.validated_data:
            if 'id' in elem and elem['id'] is not None:
                self.existing_entities_data.append(elem)
            else:
                self.new_entities_data.append(elem)
