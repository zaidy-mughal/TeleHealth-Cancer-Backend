from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings


class CustomCsrfMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Check if the path starts with any of the exempt paths
        if any(request.path.startswith(path) for path in settings.CSRF_EXEMPT_PATHS):
            setattr(request, '_dont_enforce_csrf_checks', True)  # Completely disable CSRF
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)

    def process_request(self, request):
        if any(request.path.startswith(path) for path in settings.CSRF_EXEMPT_PATHS):
            setattr(request, '_dont_enforce_csrf_checks', True)  # Completely disable CSRF
            return None
        return super().process_request(request) 