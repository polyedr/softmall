from django.contrib import admin

from .models import Function, Role, RoleFunction, UserRole


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "company", "is_active")
    list_filter = ("company", "is_active")
    search_fields = ("code", "name")


@admin.register(RoleFunction)
class RoleFunctionAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "function", "active_from", "active_to")
    list_filter = ("role", "function")
    autocomplete_fields = ("role", "function")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "active_from", "active_to")
    list_filter = ("role", "user")
    autocomplete_fields = ("user", "role")
