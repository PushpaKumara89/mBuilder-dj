from django.dispatch import Signal


post_bulk_create = Signal(providing_args=['sender', 'instances', 'created', 'update_fields', 'raw'])

post_bulk_update = Signal(providing_args=['sender', 'instances', 'update_fields'])

post_update = Signal(providing_args=['sender', 'instances', 'update_fields'])
