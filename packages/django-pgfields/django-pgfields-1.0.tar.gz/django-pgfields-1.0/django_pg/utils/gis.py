from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS


gis_backend = '.gis.' in connections[DEFAULT_DB_ALIAS].__module__
