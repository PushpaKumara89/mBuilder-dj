import os
import datetime
import time


try:
    import dateutil
except ImportError:
    dateutil = None
else:
    import dateutil.parser

from bson import DBRef
from mongoengine.connection import get_connection
from django.core.management.base import BaseCommand
from bson.objectid import ObjectId

from api.utilities.tests_utilities import load_json


class Command(BaseCommand):
    help = 'Installs the named fixture(s) in the database.'

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='fixture', nargs='+', help='Fixture labels.')

    def handle(self, *fixture_labels, **options):
        for fixture_label in fixture_labels:
            if os.path.isfile(fixture_label):
                fixture = load_json(fixture_label)
                data = self.norm_object(fixture)

                self.load_data(data)

    def norm_object(self, data):
        if isinstance(data, dict):
            if '$oid' in data:
                return ObjectId(data[u'$oid'])
            if '$ref' in data:
                return DBRef(data['$ref'], ObjectId(data['$id']))
            if '$date' in data:
                return self._parse_datetime(data['$date'])
        if isinstance(data, dict):
            return dict([(self.norm_object(k), self.norm_object(v)) for k, v in data.items()])
        if isinstance(data, list):
            return [self.norm_object(o) for o in data]
        return data

    def _parse_datetime(self, value):
        # Attempt to parse a datetime from a string
        value = value.strip()
        if not value:
            return None

        if dateutil:
            try:
                return dateutil.parser.parse(value)
            except (TypeError, ValueError, OverflowError):
                return None

        # split usecs, because they are not recognized by strptime.
        if "." in value:
            try:
                value, usecs = value.split(".")
                usecs = int(usecs)
            except ValueError:
                return None
        else:
            usecs = 0
        kwargs = {"microsecond": usecs}
        try:  # Seconds are optional, so try converting seconds first.
            return datetime.datetime(
                *time.strptime(value, "%Y-%m-%d %H:%M:%S")[:6], **kwargs
            )
        except ValueError:
            try:  # Try without seconds.
                return datetime.datetime(
                    *time.strptime(value, "%Y-%m-%d %H:%M")[:5], **kwargs
                )
            except ValueError:  # Try without hour/minutes/seconds.
                try:
                    return datetime.datetime(
                        *time.strptime(value, "%Y-%m-%d")[:3], **kwargs
                    )
                except ValueError:
                    return None

    def load_data(self, data):
        db = self.get_db()
        for obj in data:
            if '_collection' not in obj:
                raise Exception('You have to specify `_collection` field for each dump object')

            collection = obj.pop('_collection')
            collection = getattr(db, collection)

            if '_id' in obj:
                collection.replace_one({'_id': obj['_id']}, obj, upsert=True)
            else:
                collection.insert_one(obj)

    @staticmethod
    def get_db():
        return get_connection().get_default_database()
