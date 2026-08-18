from django.conf import settings
from pymongo import MongoClient


client = MongoClient(settings.MONGODB_URL)
db = client.get_default_database()