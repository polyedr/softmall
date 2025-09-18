from django.contrib import admin

from .models import (
    TimezoneDict,
    PropertyCodeDict,
    UserProperty,
    CompanyProperty,
    Module,
    CompanyModuleLicense,
)


@admin.register(TimezoneDict)
class TZAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(PropertyCodeDict)
class PropCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(UserProperty)
class UserPropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "property_code", "active_from", "active_to")
    list_filter = ("property_code",)
    autocomplete_fields = ("user", "property_code")


@admin.register(CompanyProperty)
class CompanyPropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "property_code", "active_from", "active_to")
    list_filter = ("property_code",)
    autocomplete_fields = ("company", "property_code")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(CompanyModuleLicense)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "module", "active_from", "active_to")
    list_filter = ("module", "company")
    autocomplete_fields = ("company", "module")
