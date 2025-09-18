from __future__ import annotations

from rest_framework import serializers

from .models import CompanyModuleLicense, CompanyProperty, Module, PropertyCodeDict, TimezoneDict, UserProperty


class TimezoneDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimezoneDict
        fields = ("id", "code", "name")


class PropertyCodeDictSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyCodeDict
        fields = ("id", "code", "name")


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("id", "code", "name")


class CompanyModuleLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyModuleLicense
        fields = ("id", "company", "module", "active_from", "active_to")
        read_only_fields = ("company",)


class CompanyPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProperty
        fields = ("id", "company", "property_code", "value", "active_from", "active_to")
        read_only_fields = ("company",)


class UserPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProperty
        fields = ("id", "user", "property_code", "value", "active_from", "active_to")
        read_only_fields = ("user",)
