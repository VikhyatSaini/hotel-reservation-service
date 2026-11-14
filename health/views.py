from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def live(request):
    return JsonResponse(
        {
            "status": "alive",
        }
    )


@require_GET
def ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse(
            {
                "status": "ready",
                "database": "connected",
            }
        )

    except Exception:
        return JsonResponse(
            {
                "status": "not_ready",
                "database": "unavailable",
            },
            status=503,
        )
