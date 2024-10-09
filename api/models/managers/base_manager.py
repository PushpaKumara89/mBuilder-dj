from safedelete.managers import SafeDeleteManager

from api.models.queryset import SafeDeleteQueryset


class BaseManager(SafeDeleteManager):
    def __init__(self, queryset_class=None):
        if queryset_class is None:
            queryset_class = SafeDeleteQueryset

        super().__init__(queryset_class)

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        from api.signals.models.signal import post_bulk_create

        entities = super().bulk_create(objs, batch_size, ignore_conflicts)

        post_bulk_create.send(sender=self.model, instances=objs, created=True, raw=False)

        return entities

    def bulk_update(self, objs, fields, batch_size=None):
        from api.signals.models.signal import post_bulk_update

        super().bulk_update(objs, fields, batch_size)

        ids = [obj.id for obj in objs]
        entities = list(self.filter(id__in=ids).all())
        post_bulk_update.send(sender=self.model, instances=entities, update_fields=fields)

        return entities

    def create(self, **kwargs):
        """
        Create a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(force_insert=True, using=self.db, creation=True)
        return obj

    def __getattr__(self, attr, *args):
        # see https://code.djangoproject.com/ticket/15062 for details
        if attr.startswith("_"):
            raise AttributeError
        return getattr(self.get_queryset(), attr, *args)
