from __future__ import annotations

from django.db import models
from django.utils import timezone

from accounts.models import Company, User


class Role(models.Model):
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=64)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="roles")
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "code"], name="uniq_company_role_code"),
        ]

    def __str__(self) -> str:
        return f"{self.code}@{self.company_id}"


class Function(models.Model):
    """System-wide function/permission code."""
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=64, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.code


class RoleFunction(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_functions")
    function = models.ForeignKey(Function, on_delete=models.PROTECT, related_name="role_bindings")
    active_from = models.DateTimeField(default=timezone.now)
    active_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(active_to__isnull=True) | models.Q(active_from__lte=models.F("active_to")),
                name="role_function_active_interval_valid",
            ),
            models.UniqueConstraint(fields=["role", "function", "active_from"], name="uniq_role_function_from"),
        ]


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="user_bindings")
    active_from = models.DateTimeField(default=timezone.now)
    active_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(active_to__isnull=True) | models.Q(active_from__lte=models.F("active_to")),
                name="user_role_active_interval_valid",
            ),
        ]
