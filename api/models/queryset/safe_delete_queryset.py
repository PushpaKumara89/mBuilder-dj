from safedelete.queryset import SafeDeleteQueryset as BaseSafeDeleteQueryset


class SafeDeleteQueryset(BaseSafeDeleteQueryset):
    def update(self, **kwargs):
        from api.signals.models import post_update

        # Pass only objects ids and retrieve them in signal handler because after the update
        # objects will change and we need to get their actual state.
        obj_ids = [obj.pk for obj in self]
        old_state = [obj for obj in self]
        result = super().update(**kwargs)

        post_update.send(instances=obj_ids, sender=self.model, update_fields=kwargs, old_state=old_state)

        return result

    def order_by(self, *field_names, with_default_order=True):
        if not with_default_order:
            return super().order_by(*field_names)

        order_by_fields = list(field_names)
        if any(field_name in ['pk', 'id', '-id', '-pk'] for field_name in order_by_fields):
            return super().order_by(*order_by_fields)

        order_by_fields.append('pk')

        return super().order_by(*order_by_fields)
