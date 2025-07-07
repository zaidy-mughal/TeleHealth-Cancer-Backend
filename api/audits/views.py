from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import HttpResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta
from .models import AuditLog
from .serializers import (
    AuditLogListSerializer,
    AuditLogDetailSerializer,
    # AuditLogDashboardSerializer,
    # AuditLogStatsSerializer,
    # AuditLogDashboardSerializer,
)
from .middleware import AuditLogMiddleware
import logging
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)


class AuditLogPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
    django_paginator_class = Paginator


# TODO Future modification needed according to client requirement
class AuditLogListView(generics.ListAPIView):
    """
    Audit logs filtering and pagination. Filters are user_type, action_type.
    resource_type, status, resource_id, user_name, start_date, end_date, search.
    """

    serializer_class = AuditLogListSerializer
    pagination_class = AuditLogPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = (
            AuditLog.objects.select_related("user")
            .prefetch_related("access_logs")
            .all()
        )

        params = self.request.query_params

        user_type = params.get("user_type")
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        action_type = params.get("action_type")
        if action_type:
            queryset = queryset.filter(action_type=action_type)

        resource_type = params.get("resource_type")
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        status = params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        resource_id = params.get("resource_id")
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)

        user_name = params.get("user_name")
        if user_name:
            queryset = queryset.filter(full_name__icontains=user_name)

        start_date = params.get("start_date")
        end_date = params.get("end_date")
        if start_date or end_date:
            try:
                if start_date:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                if end_date:
                    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                if start_date and end_date:
                    queryset = queryset.filter(
                        timestamp__date__range=[start_date, end_date]
                    )
                elif start_date:
                    queryset = queryset.filter(timestamp__date__gte=start_date)
                elif end_date:
                    queryset = queryset.filter(timestamp__date__lte=end_date)
            except ValueError:
                logger.warning("Invalid date format in query parameters")

        search = params.get("search")
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(action__icontains=search)
                | Q(resource_type__icontains=search)
                | Q(description__icontains=search)
                | Q(resource_id__icontains=search)
            )

        filter_log = {
            "user_type": user_type,
            "action_type": action_type,
            "resource_type": resource_type,
            "status": status,
            "resource_id": resource_id,
            "user_name": user_name,
            "start_date": start_date,
            "end_date": end_date,
            "search": search,
        }
        logger.info(f"Audit log query with filters: {filter_log}")

        return queryset.order_by("-timestamp")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(
            {
                "results": serializer.data,
                "filters_applied": request.query_params.dict(),
                "total_count": queryset.count(),
            }
        )


class AuditLogDetailView(generics.RetrieveAPIView):
    """Getting detail audit log view."""

    serializer_class = AuditLogDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = (
        AuditLog.objects.select_related("user").prefetch_related("access_logs").all()
    )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        AuditLogMiddleware()._create_audit_entry(
            request,
            None,
            {
                "action": "Viewed audit log details",
                "action_type": AuditLog.ActionTypes.READ,
                "resource_type": "Audit System",
                "resource_accessed": "Audit Log Details",
                "resource_id": str(instance.uuid),
                "status": "SUCCESS",
                "description": f"Accessed detailed view of audit log {instance.uuid}",
            },
            validate_duration(request._audit_start_time),
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# TODO
# @api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
# @cache_page(60 * 15)
# def audit_dashboard_view(request):
#     """
#     API endpoint for audit dashboard with aggregated data and caching.
#     """
#     try:
#         cache_key = f"audit_dashboard_{request.user.id}_{request.query_params}"
#         cached_data = cache.get(cache_key)
#         if cached_data:
#             return Response(cached_data)

#         start_date = request.query_params.get("start_date")
#         end_date = request.query_params.get("end_date")
#         user_type = request.query_params.get("user_type")

#         if start_date:
#             start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
#         if end_date:
#             end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

#         dashboard_data = get_dashboard_data(start_date, end_date, user_type)
#         serializer = AuditLogDashboardSerializer(dashboard_data, many=True)

#         AuditLogMiddleware()._create_audit_entry(
#             request,
#             None,
#             {
#                 "action": "Accessed audit dashboard",
#                 "action_type": AuditLog.ActionTypes.READ,
#                 "resource_type": "Audit System",
#                 "resource_accessed": "Audit Dashboard",
#                 "status": "SUCCESS",
#                 "description": f"Viewed audit dashboard with filters: {request.query_params}",
#             },
#             validate_duration(request._audit_start_time),
#         )

#         response_data = {
#             "results": serializer.data,
#             "count": len(serializer.data),
#             "filters": {
#                 "start_date": start_date.isoformat() if start_date else None,
#                 "end_date": end_date.isoformat() if end_date else None,
#                 "user_type": user_type,
#             },
#         }
#         cache.set(cache_key, response_data, 60 * 15)
#         return Response(response_data)

#     except Exception as e:
#         logger.error(f"Dashboard error: {str(e)}")
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
# @cache_page(60 * 15)
# def audit_statistics_view(request):
#     """
#     API endpoint for audit statistics with caching.
#     """
#     try:
#         cache_key = (
#             f"audit_stats_{request.user.id}_{request.query_params.get('days', 30)}"
#         )
#         cached_data = cache.get(cache_key)
#         if cached_data:
#             return Response(cached_data)

#         days = int(request.query_params.get("days", 30))
#         end_date = timezone.now()
#         start_date = end_date - timedelta(days=days)
#         stats = {
#             "total_logs": AuditLog.objects.count(),
#             "logs_today": AuditLog.objects.filter(
#                 timestamp__date=timezone.now().date()
#             ).count(),
#             "logs_this_week": AuditLog.objects.filter(
#                 timestamp__date__range=[start_date.date(), end_date.date()]
#             ).count(),
#             "logs_this_month": AuditLog.objects.filter(
#                 timestamp__month=timezone.now().month
#             ).count(),
#             "top_users": list(
#                 AuditLog.objects.values("user__username")
#                 .annotate(total=Count("uuid"))
#                 .order_by("-total")[:5]
#             ),
#             "action_breakdown": dict(
#                 AuditLog.objects.values("action_type")
#                 .annotate(count=Count("uuid"))
#                 .values_list("action_type", "count")
#             ),
#             "recent_activities": list(
#                 AuditLog.objects.order_by("-timestamp")[:10].values(
#                     "full_name", "action", "timestamp", "resource_type"
#                 )
#             ),
#             "failed_actions": AuditLog.objects.filter(status="FAILED").count(),
#             "avg_session_duration": str(
#                 AuditLog.objects.aggregate(avg=Sum("duration_seconds") / Count("uuid"))[
#                     "avg"
#                 ]
#                 or 0
#             ),
#         }

#         serializer = AuditLogStatsSerializer(stats)
#         AuditLogMiddleware()._create_audit_entry(
#             request,
#             None,
#             {
#                 "action": "Viewed audit statistics",
#                 "action_type": AuditLog.ActionTypes.READ,
#                 "resource_type": "Audit System",
#                 "resource_accessed": "Audit Statistics",
#                 "status": "SUCCESS",
#                 "description": f"Accessed audit statistics for {days} days",
#             },
#             validate_duration(request._audit_start_time),
#         )

#         cache.set(cache_key, serializer.data, 60 * 15)
#         return Response(serializer.data)
#     except Exception as e:
#         logger.error(f"Statistics error: {str(e)}")
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
# def export_audit_logs_view(request):
#     """
#     API endpoint to export audit logs (inline export logic).
#     """
#     try:
#         start_date = request.query_params.get("start_date")
#         end_date = request.query_params.get("end_date")
#         user_type = request.query_params.get("user_type")
#         format_type = request.query_params.get("format", "csv").lower()

#         if not start_date or not end_date:
#             return Response(
#                 {"error": "start_date and end_date are required"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
#         end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

#         queryset = AuditLog.objects.filter(
#             timestamp__date__range=[start_date, end_date]
#         )
#         if user_type:
#             queryset = queryset.filter(user_type=user_type)

#         data = list(
#             queryset.values(
#                 "full_name",
#                 "action",
#                 "action_type",
#                 "resource_type",
#                 "resource_id",
#                 "status",
#                 "timestamp",
#                 "ip_address",
#                 "user_agent",
#                 "session_id",
#                 "description",
#             )
#         )

#         if format_type == "csv":
#             import csv
#             from io import StringIO

#             output = StringIO()
#             writer = csv.DictWriter(output, fieldnames=data[0].keys())
#             writer.writeheader()
#             writer.writerows(data)
#             response = HttpResponse(output.getvalue(), content_type="text/csv")
#             response["Content-Disposition"] = (
#                 f'attachment; filename="audit_logs_{start_date}_to_{end_date}.csv"'
#             )
#         else:
#             return Response(
#                 {"error": "Unsupported format"}, status=status.HTTP_400_BAD_REQUEST
#             )

#         AuditLogMiddleware()._create_audit_entry(
#             request,
#             None,
#             {
#                 "action": "Exported audit logs",
#                 "action_type": AuditLog.ActionTypes.READ,
#                 "resource_type": "Audit System",
#                 "resource_accessed": "Audit Export",
#                 "status": "SUCCESS",
#                 "description": f"Exported audit logs from {start_date} to {end_date}",
#             },
#             validate_duration(request._audit_start_time),
#         )

#         return response
#     except Exception as e:
#         logger.error(f"Export error: {str(e)}")
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
