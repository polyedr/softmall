from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EffectiveSettingView, SettingDictViewSet, SettingValueViewSet

router = DefaultRouter()
router.register("dict", SettingDictViewSet, basename="setting-dict")
router.register("values", SettingValueViewSet, basename="setting-value")

urlpatterns = router.urls + [
    path("effective/<str:code>", EffectiveSettingView.as_view(), name="settings-effective"),
]
