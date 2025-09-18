from __future__ import annotations


from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class Company(models.Model):
    """Tenant/company with active period and licensing flags."""
    name = models.CharField(max_length=255, unique=True)
    inn = models.CharField(max_length=12, blank=True)
    is_active = models.BooleanField(default=True)
    active_from = models.DateTimeField(default=timezone.now)
    active_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(active_to__isnull=True) | models.Q(active_from__lte=models.F("active_to")),
                name="company_active_interval_valid",
            ),
        ]

    def __str__(self) -> str:
        return self.name


username_validator = RegexValidator(r"^[\w.@+-]+$", "Enter a valid username.")


class User(AbstractUser):
    """Custom user bound to a company (tenant)."""
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="users", null=True, blank=True)
    is_locked = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "username"], name="uniq_company_username"),
        ]

    def __str__(self) -> str:
        return f"{self.username} ({self.company_id})"
