from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import mixins, permissions, viewsets

from common.permissions import HasFunction

from .models import CompanyModuleLicense, CompanyProperty, Module, PropertyCodeDict, TimezoneDict, UserProperty
from .serializers import (
    CompanyModuleLicenseSerializer,
    CompanyPropertySerializer,
    ModuleSerializer,
    PropertyCodeDictSerializer,
    TimezoneDictSerializer,
    UserPropertySerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["catalogs"], description="Справочник часовых поясов."),
)
class TimezoneDictViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TimezoneDict.objects.all().order_by("id")
    serializer_class = TimezoneDictSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:view")]
    pagination_class = None


@extend_schema_view(
    list=extend_schema(tags=["catalogs"], description="Список кодов свойств."),
    create=extend_schema(
        tags=["catalogs"],
        description="Создать код свойства.",
        request=PropertyCodeDictSerializer,
        responses={201: PropertyCodeDictSerializer},
    ),
    update=extend_schema(
        tags=["catalogs"],
        description="Обновить код свойства.",
        request=PropertyCodeDictSerializer,
        responses={200: PropertyCodeDictSerializer},
    ),
    partial_update=extend_schema(
        tags=["catalogs"],
        description="Частично обновить код свойства.",
        request=PropertyCodeDictSerializer,
        responses={200: PropertyCodeDictSerializer},
    ),
    destroy=extend_schema(
        tags=["catalogs"], description="Удалить код свойства.", responses={204: OpenApiResponse(description="Deleted")}
    ),
)
class PropertyCodeDictViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = PropertyCodeDict.objects.all().order_by("id")
    serializer_class = PropertyCodeDictSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]
    pagination_class = None


@extend_schema_view(
    list=extend_schema(tags=["catalogs"], description="Список модулей."),
    create=extend_schema(
        tags=["catalogs"], description="Создать модуль.", request=ModuleSerializer, responses={201: ModuleSerializer}
    ),
    update=extend_schema(
        tags=["catalogs"], description="Обновить модуль.", request=ModuleSerializer, responses={200: ModuleSerializer}
    ),
    partial_update=extend_schema(
        tags=["catalogs"],
        description="Частично обновить модуль.",
        request=ModuleSerializer,
        responses={200: ModuleSerializer},
    ),
    destroy=extend_schema(
        tags=["catalogs"], description="Удалить модуль.", responses={204: OpenApiResponse(description="Deleted")}
    ),
)
class ModuleViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Module.objects.all().order_by("id")
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]
    pagination_class = None


@extend_schema_view(
    list=extend_schema(tags=["catalogs"], description="Лицензии модулей компании (данные только вашей компании)."),
    create=extend_schema(
        tags=["catalogs"],
        description="Выдать/продлить лицензию модулю компании.",
        request=CompanyModuleLicenseSerializer,
        responses={201: CompanyModuleLicenseSerializer},
    ),
    update=extend_schema(
        tags=["catalogs"],
        description="Обновить запись лицензии.",
        request=CompanyModuleLicenseSerializer,
        responses={200: CompanyModuleLicenseSerializer},
    ),
    partial_update=extend_schema(
        tags=["catalogs"],
        description="Частично обновить запись лицензии.",
        request=CompanyModuleLicenseSerializer,
        responses={200: CompanyModuleLicenseSerializer},
    ),
    destroy=extend_schema(
        tags=["catalogs"],
        description="Удалить запись лицензии.",
        responses={204: OpenApiResponse(description="Deleted")},
    ),
)
class CompanyModuleLicenseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CompanyModuleLicenseSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]
    pagination_class = None

    def get_queryset(self):
        return (
            CompanyModuleLicense.objects.select_related("company", "module")
            .filter(company_id=self.request.user.company_id)
            .order_by("-active_from")
        )

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


@extend_schema_view(
    list=extend_schema(tags=["catalogs"], description="Свойства компании (данные только вашей компании)."),
    create=extend_schema(
        tags=["catalogs"],
        description="Создать свойство компании.",
        request=CompanyPropertySerializer,
        responses={201: CompanyPropertySerializer},
    ),
    update=extend_schema(
        tags=["catalogs"],
        description="Обновить свойство компании.",
        request=CompanyPropertySerializer,
        responses={200: CompanyPropertySerializer},
    ),
    partial_update=extend_schema(
        tags=["catalogs"],
        description="Частично обновить свойство компании.",
        request=CompanyPropertySerializer,
        responses={200: CompanyPropertySerializer},
    ),
    destroy=extend_schema(
        tags=["catalogs"],
        description="Удалить свойство компании.",
        responses={204: OpenApiResponse(description="Deleted")},
    ),
)
class CompanyPropertyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CompanyPropertySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]
    pagination_class = None

    def get_queryset(self):
        return (
            CompanyProperty.objects.select_related("company", "property_code")
            .filter(company_id=self.request.user.company_id)
            .order_by("-active_from")
        )

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


@extend_schema_view(
    list=extend_schema(tags=["catalogs"], description="Свойства пользователей вашей компании."),
    create=extend_schema(
        tags=["catalogs"],
        description="Создать свойство пользователя.",
        request=UserPropertySerializer,
        responses={201: UserPropertySerializer},
    ),
    update=extend_schema(
        tags=["catalogs"],
        description="Обновить свойство пользователя.",
        request=UserPropertySerializer,
        responses={200: UserPropertySerializer},
    ),
    partial_update=extend_schema(
        tags=["catalogs"],
        description="Частично обновить свойство пользователя.",
        request=UserPropertySerializer,
        responses={200: UserPropertySerializer},
    ),
    destroy=extend_schema(
        tags=["catalogs"],
        description="Удалить свойство пользователя.",
        responses={204: OpenApiResponse(description="Deleted")},
    ),
)
class UserPropertyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserPropertySerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]
    pagination_class = None

    def get_queryset(self):
        return (
            UserProperty.objects.select_related("user", "property_code")
            .filter(user__company_id=self.request.user.company_id)
            .order_by("-active_from")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
