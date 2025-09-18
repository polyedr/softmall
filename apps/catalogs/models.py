from __future__ import annotations

from django.db import models
from django.utils import timezone

from accounts.models import Company, User


class TimezoneDict(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.code


class PropertyCodeDict(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.code


class UserProperty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    property_code = models.ForeignKey(PropertyCodeDict, on_delete=models.PROTECT, related_name="user_values")
    value = models.JSONField()
    active_from = models.DateTimeField(default=timezone.now)
    active_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "property_code", "active_from"], name="uniq_user_prop_from"),
            models.CheckConstraint(
                check=models.Q(active_to__isnull=True) | models.Q(active_from__lte=models.F("active_to")),
                name="user_prop_active_interval_valid",
            ),
        ]


class CompanyProperty(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="properties")
    property_code = models.ForeignKey(PropertyCodeDict, on_delete=models.PROTECT, related_name="company_values")
    value = models.JSONField()
    active_from = models.DateTimeField(default=timezone.now)
    active_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "property_code", "active_from"], name="uniq_company_prop_from"),
            models.CheckConstraint(
                check=models.Q(active_to__isnull=True) | models.Q(active_from__lte=models.F("active_to")),
                name="company_prop_active_interval_valid",
            ),
        ]


class Module(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.code


class CompanyModuleLicense(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="module_licenses")
    module = models.ForeignKey(Module, on_delete=models.PROTECT, related_name="company_licenses")
    active_from = models.DateTimeField(default=timezone.now)
    active_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "module", "active_from"], name="uniq_company_module_from"),
            models.CheckConstraint(
                check=models.Q(active_to__isnull=True) | models.Q(active_from__lte=models.F("active_to")),
                name="company_module_active_interval_valid",
            ),
        ]
