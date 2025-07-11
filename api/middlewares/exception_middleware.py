import traceback
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware:
    """
    Catches all unhandled exceptions and returns a JSON error response.
    Used as a safety net to catch anything not handled by DRF or view-level logic.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)

            if response is None:
                logger.warning("View returned None; unexpected behavior.")
                return JsonResponse(
                    {
                        "type": "server_error",
                        "errors": {
                            "non_field_errors": ["An unexpected error occurred."]
                        },
                    },
                    status=500,
                )

            return response

        except Exception as exc:
            logger.critical("Unhandled Exception:\n%s", traceback.format_exc())

            return JsonResponse(
                {
                    "type": "server_error",
                    "errors": {"non_field_errors": ["An unexpected error occurred."]},
                },
                status=500,
            )
