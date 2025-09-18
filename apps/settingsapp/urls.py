from django.urls import path
from .views import EffectiveSettingView, SettingDictViewSet, SettingValueViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register("dict", SettingDictViewSet, basename="setting-dict")
router.register("values", SettingValueViewSet, basename="setting-value")

urlpatterns = router.urls + [
    path("effective/<str:code>", EffectiveSettingView.as_view(), name="settings-effective"),
]
