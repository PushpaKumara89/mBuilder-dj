import json


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def load_mongo_json(path):
    from bson.json_util import loads

    with open(path, 'r') as f:
        return loads(json.load(f))


def load_fixture(path):
    with open(path, 'r') as f:
        return f.read()
