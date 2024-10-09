from django.db.models import DateTimeField


class DateTimeFieldOmitAutoNowValue(DateTimeField):
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)

        if value is None:
            return super().pre_save(model_instance, add)

        return value
