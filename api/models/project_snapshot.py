from mongoengine import *


class ProjectSnapshot(Document):
    data = DictField(required=True)
    generation_started_at = DateTimeField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)
    project_id = IntField(required=True)
