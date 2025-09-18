from __future__ import annotations

from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import HasFunction
from rbac.models import Function, Role, RoleFunction

from .serializers import AssignUserRoleSerializer, FunctionSerializer, RoleFunctionSerializer, RoleSerializer


@extend_schema_view(
    list=extend_schema(tags=["rbac"], description="Список функций."),
    retrieve=extend_schema(tags=["rbac"], description="Получить функцию."),
    create=extend_schema(
        tags=["rbac"], description="Создать функцию.", request=FunctionSerializer, responses={201: FunctionSerializer}
    ),
    update=extend_schema(
        tags=["rbac"],
        description="Полное обновление функции.",
        request=FunctionSerializer,
        responses={200: FunctionSerializer},
    ),
    partial_update=extend_schema(
        tags=["rbac"],
        description="Частичное обновление функции.",
        request=FunctionSerializer,
        responses={200: FunctionSerializer},
    ),
    destroy=extend_schema(
        tags=["rbac"], description="Удалить функцию.", responses={204: OpenApiResponse(description="Deleted")}
    ),
)
class FunctionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Function.objects.all()
    serializer_class = FunctionSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]


@extend_schema_view(
    list=extend_schema(tags=["rbac"], description="Список ролей."),
    retrieve=extend_schema(tags=["rbac"], description="Получить роль."),
    create=extend_schema(
        tags=["rbac"], description="Создать роль.", request=RoleSerializer, responses={201: RoleSerializer}
    ),
    update=extend_schema(
        tags=["rbac"], description="Полное обновление роли.", request=RoleSerializer, responses={200: RoleSerializer}
    ),
    partial_update=extend_schema(
        tags=["rbac"],
        description="Частичное обновление роли.",
        request=RoleSerializer,
        responses={200: RoleSerializer},
    ),
    destroy=extend_schema(
        tags=["rbac"], description="Удалить роль.", responses={204: OpenApiResponse(description="Deleted")}
    ),
)
class RoleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Role.objects.select_related("company").all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]

    @extend_schema(
        tags=["rbac"],
        request=RoleFunctionSerializer,
        responses={201: RoleFunctionSerializer},
        description="Привязать функцию к роли с интервалом активности.",
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="functions",
        permission_classes=[permissions.IsAuthenticated, HasFunction.required("users:edit")],
    )
    def add_function(self, request, pk=None):
        payload = {
            "role": pk,
            "function": request.data.get("function"),
            "active_from": request.data.get("active_from"),
            "active_to": request.data.get("active_to"),
        }
        if not payload["active_from"]:
            payload["active_from"] = timezone.now()

        serializer = RoleFunctionSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(RoleFunctionSerializer(obj).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(tags=["rbac"], description="Список привязок роль→функция."),
    retrieve=extend_schema(tags=["rbac"], description="Получить привязку роль→функция."),
)
class RoleFunctionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = RoleFunction.objects.select_related("role", "function").all()
    serializer_class = RoleFunctionSerializer
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:view")]
    pagination_class = None


class AssignUserRoleViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, HasFunction.required("users:edit")]

    @extend_schema(
        tags=["rbac"],
        request=AssignUserRoleSerializer,
        responses={201: dict},
        description="Назначить роль пользователю с датой начала активности.",
    )
    def create(self, request):
        serializer = AssignUserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data, status=status.HTTP_201_CREATED)
