from drf_yasg import openapi

event_id_param = openapi.Parameter(
    "event_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True
)

event_parameter = openapi.Parameter(
    "event",
    openapi.IN_QUERY,
    type=openapi.TYPE_OBJECT,
    required=True,
)
