from __future__ import annotations

from django.conf import settings
from django.db import models


class IdempotencyKey(models.Model):
    key = models.CharField(max_length=128, unique=True)
    endpoint = models.CharField(max_length=255)
    request_hash = models.CharField(max_length=64)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    status_code = models.PositiveIntegerField()
    response_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["key", "endpoint"], name="ix_idem_key_endpoint"),
        ]
