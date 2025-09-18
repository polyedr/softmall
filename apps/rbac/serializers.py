from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers

from rbac.models import Function, Role, RoleFunction, UserRole
from accounts.models import User


class FunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Function
        fields = ("id", "code", "name", "is_active")


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "code", "name", "company", "is_active")


class RoleFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleFunction
        fields = ("id", "role", "function", "active_from", "active_to")


class AssignUserRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()
    active_from = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        if not User.objects.filter(id=attrs["user_id"]).exists():
            raise serializers.ValidationError("User not found.")
        if not Role.objects.filter(id=attrs["role_id"]).exists():
            raise serializers.ValidationError("Role not found.")
        return attrs

    def create(self, validated_data):
        now = validated_data.get("active_from") or timezone.now()
        obj, _ = UserRole.objects.get_or_create(
            user_id=validated_data["user_id"],
            role_id=validated_data["role_id"],
            active_from=now,
        )
        return {"user_role_id": obj.id}
