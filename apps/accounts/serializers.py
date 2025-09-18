from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers

from accounts.models import Company, User
from rbac.models import Function, Role, RoleFunction, UserRole


class RegisterCompanySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    admin_username = serializers.CharField(max_length=150)
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        now = timezone.now()
        company, _ = Company.objects.get_or_create(
            name=validated_data["name"],
            defaults={"active_from": now},
        )
        user, created = User.objects.get_or_create(
            username=validated_data["admin_username"],
            defaults={
                "email": validated_data["admin_email"],
                "company": company,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        if created:
            user.set_password(validated_data["admin_password"])
            user.save()

        # базовая роль admin и функции
        role, _ = Role.objects.get_or_create(company=company, code="admin", defaults={"name": "Administrator"})
        for code, name in [
            ("users:view", "View users"),
            ("users:edit", "Edit users"),
            ("settings:view", "View settings"),
        ]:
            fn, _ = Function.objects.get_or_create(code=code, defaults={"name": name})
            RoleFunction.objects.get_or_create(role=role, function=fn, defaults={"active_from": now})
        UserRole.objects.get_or_create(user=user, role=role, defaults={"active_from": now})

        return {"company_id": company.id, "admin_id": user.id}


class RegisterUserSerializer(serializers.Serializer):
    company_id = serializers.IntegerField()
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_company_id(self, value):
        if not Company.objects.filter(id=value).exists():
            raise serializers.ValidationError("Company not found.")
        return value

    def create(self, validated_data):
        company = Company.objects.get(id=validated_data["company_id"])
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            company=company,
            is_active=True,
        )
        user.set_password(validated_data["password"])
        user.save()
        return {"user_id": user.id}


class MeSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    functions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "company", "is_staff", "is_superuser", "roles", "functions")

    def get_roles(self, obj):
        now = timezone.now()
        qs = obj.user_roles.filter(active_from__lte=now).filter(active_to__isnull=True) | obj.user_roles.filter(
            active_to__gte=now
        )
        return list(qs.values_list("role__code", flat=True).distinct())

    def get_functions(self, obj):
        now = timezone.now()
        role_ids = obj.user_roles.filter(active_from__lte=now).filter(active_to__isnull=True) | obj.user_roles.filter(
            active_to__gte=now
        )
        role_ids = role_ids.values_list("role_id", flat=True)
        fns = RoleFunction.objects.filter(
            role_id__in=role_ids,
            active_from__lte=now,
        ).filter(
            active_to__isnull=True
        ) | RoleFunction.objects.filter(role_id__in=role_ids, active_to__gte=now)
        return list(fns.values_list("function__code", flat=True).distinct())
