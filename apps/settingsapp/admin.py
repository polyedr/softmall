from django.contrib import admin

from .models import SettingDict, SettingValue


@admin.register(SettingDict)
class SettingDictAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(SettingValue)
class SettingValueAdmin(admin.ModelAdmin):
    list_display = ("id", "setting", "company", "user", "active_from", "active_to")
    list_filter = ("setting", "company")
    autocomplete_fields = ("setting", "company", "user")
