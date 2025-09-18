from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyModuleLicenseViewSet,
    CompanyPropertyViewSet,
    ModuleViewSet,
    PropertyCodeDictViewSet,
    TimezoneDictViewSet,
    UserPropertyViewSet,
)

router = DefaultRouter()
router.register("timezones", TimezoneDictViewSet, basename="tz")
router.register("property-codes", PropertyCodeDictViewSet, basename="prop-codes")
router.register("modules", ModuleViewSet, basename="modules")
router.register("company-licenses", CompanyModuleLicenseViewSet, basename="company-licenses")
router.register("company-properties", CompanyPropertyViewSet, basename="company-properties")
router.register("user-properties", UserPropertyViewSet, basename="user-properties")

urlpatterns = router.urls
