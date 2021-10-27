from drf_yasg import openapi

event_id_param = openapi.Parameter(
    "event_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True
)
