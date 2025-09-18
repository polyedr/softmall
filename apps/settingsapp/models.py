from __future__ import annotations

from django.db import models
from django.utils import timezone

from accounts.models import Company, User


class SettingDict(models.Model):
    """Dictionary of available settings."""
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.code


class SettingValue(models.Model):
    """Actual setting values scoped to user or company, with active intervals."""
    setting = models.ForeignKey(SettingDict, on_delete=models.CASCADE, related_name="values")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="settings", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="settings", null=True, blank=True)
    value = models.JSONField()
    active_from = models.DateTimeField(default=timezone.now)
    active_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(active_to__isnull=True) | models.Q(active_from__lte=models.F("active_to")),
                name="setting_value_active_interval_valid",
            ),
            models.CheckConstraint(
                check=models.Q(company__isnull=False) | models.Q(user__isnull=False),
                name="setting_value_has_owner",
            ),
            models.UniqueConstraint(
                fields=["setting", "company", "user", "active_from"],
                name="uniq_setting_owner_from",
            ),
        ]
