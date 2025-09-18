# Creating thte superadmin account if not existed
# Seeding the database with initial data
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Company, User
from catalogs.models import CompanyModuleLicense, Module
from rbac.models import Function, Role, RoleFunction, UserRole
from settingsapp.models import SettingDict, SettingValue


class Command(BaseCommand):
    help = "Seed initial data for demo/testing"

    def handle(self, *args, **options):
        now = timezone.now()

        company, _ = Company.objects.get_or_create(
            name="Soft Corp",
            defaults={"active_from": now},
        )

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "company": company,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        if created:
            admin.set_password("admin")
            admin.save()
        self.stdout.write(self.style.SUCCESS(f"Admin user: {admin.username}/admin"))

        func_codes = [
            ("users:view", "Просмотр пользователей"),
            ("users:edit", "Редактирование пользователей"),
            ("settings:view", "Просмотр настроек"),
        ]
        functions = []
        for code, name in func_codes:
            fn, _ = Function.objects.get_or_create(code=code, defaults={"name": name})
            functions.append(fn)

        role, _ = Role.objects.get_or_create(
            company=company,
            code="admin",
            defaults={"name": "Администратор"},
        )

        for fn in functions:
            RoleFunction.objects.get_or_create(role=role, function=fn, active_from=now)

        UserRole.objects.get_or_create(user=admin, role=role, active_from=now)

        sdict, _ = SettingDict.objects.get_or_create(code="theme", defaults={"name": "Theme"})
        SettingValue.objects.get_or_create(
            setting=sdict,
            company=company,
            defaults={"value": {"color": "light"}, "active_from": now},
        )

        module, _ = Module.objects.get_or_create(code="analytics", defaults={"name": "Analytics"})
        CompanyModuleLicense.objects.get_or_create(
            company=company,
            module=module,
            defaults={"active_from": now},
        )

        self.stdout.write(self.style.SUCCESS("Seed data created."))
