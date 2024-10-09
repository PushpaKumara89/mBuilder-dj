from typing import Dict

from api.models.project_news import ProjectNews
from api.services.base_entity_service import BaseEntityService


class ProjectNewsEntityService(BaseEntityService):
    model: ProjectNews = ProjectNews

    def create(self, validated_data: Dict) -> ProjectNews:
        validated_data['project'] = validated_data.pop('project_id')
        return self.model.objects.create(**validated_data)

    def update(self, instance: ProjectNews, validated_data: Dict) -> ProjectNews:
        if 'project_id' in validated_data:
            validated_data['project'] = validated_data.pop('project_id')
        return super().update(instance, validated_data)
