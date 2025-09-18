from __future__ import annotations

from datetime import datetime, timezone

from django.db import models
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class HasFunction(BasePermission):
    """Checks that the authenticated user has an active function (permission code)
    effective at *now* within their company context.

    Usage:
        class MyView(...):
            permission_classes = [HasFunction.required("users:view")]
    """
    required_code: str | None = None

    @classmethod
    def required(cls, code: str) -> type["HasFunction"]:
        class _Req(cls):
            required_code = code
        return _Req

    def has_permission(self, request: Request, view: View) -> bool:
        user = getattr(request, "user", None)
        code = getattr(self, "required_code", None)
        if not user or not user.is_authenticated or not code:
            return False

        now = datetime.now(timezone.utc)

        # Lazy import to avoid circular deps
        from rbac.models import Function, RoleFunction, UserRole

        try:
            fn = Function.objects.get(code=code, is_active=True)
        except Function.DoesNotExist:
            return False

        roles_qs = (
            UserRole.objects.filter(user=user, active_from__lte=now)
            .filter(models.Q(active_to__isnull=True) | models.Q(active_to__gte=now))
        )
        if not roles_qs.exists():
            return False

        rf_qs = (
            RoleFunction.objects.filter(
                role_id__in=roles_qs.values_list("role_id", flat=True),
                function=fn,
                active_from__lte=now,
            )
            .filter(models.Q(active_to__isnull=True) | models.Q(active_to__gte=now))
        )
        return rf_qs.exists()
