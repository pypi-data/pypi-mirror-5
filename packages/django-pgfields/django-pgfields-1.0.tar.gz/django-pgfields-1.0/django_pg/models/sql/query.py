from django.db.models.sql import query
from django.contrib.gis.db.models.sql import query as gis_query


DJANGO_PG_QUERY_TERMS = { 'len' }


class Query(query.Query):
    query_terms = query.Query.query_terms.union(DJANGO_PG_QUERY_TERMS)


class GeoQuery(gis_query.GeoQuery):
    query_terms = gis_query.GeoQuery.query_terms.union(DJANGO_PG_QUERY_TERMS)
