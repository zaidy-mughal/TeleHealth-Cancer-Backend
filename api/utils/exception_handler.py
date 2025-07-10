import traceback
import logging
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
    NotAuthenticated,
    PermissionDenied as DRFPermissionDenied,
    NotFound,
    ParseError,
    Throttled,
    UnsupportedMediaType,
)
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
    PermissionDenied as DjangoPermissionDenied,
    ObjectDoesNotExist,
)

logger = logging.getLogger(__name__)


def format_error_detail(detail):
    if isinstance(detail, list):
        return [format_error_detail(item) for item in detail]
    elif isinstance(detail, dict):
        return {key: format_error_detail(value) for key, value in detail.items()}
    else:
        return str(detail)


class _HandleExceptionMixin:
    """
    Mixin that provides a unified handle_exception method for DRF views and viewsets.
    """

    def handle_exception(self, exc):
        if isinstance(exc, (DRFValidationError, DjangoValidationError)):
            logger.warning(f"Validation error: {exc}")
            detail = getattr(exc, "detail", str(exc))
            formatted = format_error_detail(detail)
            return Response({"errors": formatted}, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(exc, (DRFPermissionDenied, DjangoPermissionDenied)):
            logger.warning(f"Permission denied: {exc}")
            return Response(
                {"errors": {"non_field_errors": [str(exc)]}},
                status=status.HTTP_403_FORBIDDEN,
            )

        elif isinstance(exc, NotAuthenticated):
            logger.warning(f"Authentication required: {exc}")
            return Response(
                {"errors": {"non_field_errors": [str(exc)]}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        elif isinstance(exc, ObjectDoesNotExist):
            logger.warning(f"Object not found: {exc}")
            return Response(
                {"errors": {"non_field_errors": ["Resource not found."]}},
                status=status.HTTP_404_NOT_FOUND,
            )

        elif isinstance(exc, NotFound):
            logger.warning(f"Resource not found: {exc}")
            return Response(
                {"errors": {"non_field_errors": [str(exc)]}},
                status=status.HTTP_404_NOT_FOUND,
            )

        elif isinstance(exc, (ParseError, Throttled, UnsupportedMediaType)):
            logger.warning(f"Client error: {exc}")
            return Response(
                {"errors": {"non_field_errors": [str(exc)]}},
                status=getattr(exc, "status_code", 400),
            )

        logger.critical("Unhandled Exception:\n%s", traceback.format_exc())
        return Response(
            {"errors": {"non_field_errors": ["An unexpected error occurred."]}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class HandleExceptionAPIView(_HandleExceptionMixin, APIView):
    """
    Base class for DRF APIViews with standardized exception handling.
    Use in place of APIView or GenericAPIView.
    """
    pass


class HandleExceptionViewset(_HandleExceptionMixin, GenericViewSet):
    """
    Base class for DRF ViewSets with standardized exception handling.
    Use in place of ViewSet, GenericViewSet, ModelViewSet.
    """
    pass
