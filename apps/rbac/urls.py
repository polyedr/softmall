from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AssignUserRoleViewSet, FunctionViewSet, RoleFunctionViewSet, RoleViewSet


router = DefaultRouter()
router.register("functions", FunctionViewSet, basename="function")
router.register("roles", RoleViewSet, basename="role")
router.register("role-functions", RoleFunctionViewSet, basename="role-function")

urlpatterns = [
    path("", include(router.urls)),
    path("assign-role", AssignUserRoleViewSet.as_view({"post": "create"}), name="assign-role"),
]
