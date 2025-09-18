from __future__ import annotations

from django.apps import AppConfig


class SettingsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "settingsapp"
    label = "settingsapp"
