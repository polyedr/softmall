from __future__ import annotations

from rest_framework import serializers

from .models import SettingDict, SettingValue


class SettingDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingDict
        fields = ("id", "code", "name", "description")


class SettingValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingValue
        fields = ("id", "setting", "company", "user", "value", "active_from", "active_to")
        read_only_fields = ("company", "user")
