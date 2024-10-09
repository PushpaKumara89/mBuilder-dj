from typing import Dict, Optional

from api.models import AppSettings


class AppSettingsService:
    model: AppSettings = AppSettings

    def __init__(self, instance: Optional[AppSettings] = None) -> None:
        self.instance = instance

    @classmethod
    def get_or_create(cls, init_data: Dict = None) -> AppSettings:
        if not init_data:
            init_data = {
                'disable_user_registration_from_mobile_devices': False
            }

        insatnce = cls.model.objects.first()
        if insatnce:
            return insatnce

        return cls.model.objects.create(**init_data)

    def update(self, validation_data: Dict) -> AppSettings:
        assert self.instance is not None

        update_fields = []
        for field, value in validation_data.items():
            if hasattr(self.instance, field) and getattr(self.instance, field) != value:
                setattr(self.instance, field, value)
                update_fields.append(field)

        if update_fields:
            self.instance.save(update_fields=update_fields)

        return self.instance
