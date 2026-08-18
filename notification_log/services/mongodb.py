from django.conf import settings
from pymongo import MongoClient


_client = None


def get_client():
    global _client

    if _client is None:
        _client = MongoClient(settings.MONGODB_URL)

    return _client


def get_db():
    return get_client().get_default_database()